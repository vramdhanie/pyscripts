import argparse
import os
import sys
from typing import Any


# Full Drive scope to allow reading and creating copies
SCOPES: list[str] = ["https://www.googleapis.com/auth/drive"]

FOLDER_MIME_TYPE: str = "application/vnd.google-apps.folder"


def build_drive_service(credentials_path: str, token_path: str):
    """
    Build an authenticated Google Drive service using OAuth credentials.
    The token file is created/updated as needed to preserve the session.
    """
    # Local imports to avoid hard dependency at module import time
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build

    creds: Credentials | None = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(credentials_path):
                raise FileNotFoundError(f"Missing OAuth client secrets file at '{credentials_path}'. Download it from Google Cloud Console (OAuth client ID JSON).")
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, "w") as token_file:
            _ = token_file.write(creds.to_json())

    return build("drive", "v3", credentials=creds, cache_discovery=False)


def get_file_metadata(service: Any, file_id: str, fields: str = "id, name, mimeType, parents") -> dict:
    return (
        service.files()
        .get(fileId=file_id, fields=fields, supportsAllDrives=True)
        .execute(num_retries=5)
    )


def is_folder(metadata: dict) -> bool:
    return metadata.get("mimeType") == FOLDER_MIME_TYPE


def list_children(
    service: Any,
    folder_id: str,
    include_trashed: bool = False,
    fields: str = "nextPageToken, files(id, name, mimeType)",
) -> list[dict]:
    """
    List immediate children of the given folder.
    """
    q_parts: list[str] = [f"'{folder_id}' in parents"]
    if not include_trashed:
        q_parts.append("trashed=false")
    query = " and ".join(q_parts)

    children: list[dict] = []
    page_token: str | None = None

    while True:
        response = (
            service.files()
            .list(
                q=query,
                spaces="drive",
                fields=fields,
                pageToken=page_token,
                supportsAllDrives=True,
                includeItemsFromAllDrives=True,
                corpora="user",
            )
            .execute(num_retries=5)
        )
        children.extend(response.get("files", []))
        page_token = response.get("nextPageToken")
        if not page_token:
            break
    return children


def create_folder(service: Any, name: str, parent_id: str) -> dict:
    body = {
        "name": name,
        "mimeType": FOLDER_MIME_TYPE,
        "parents": [parent_id],
    }
    return (
        service.files()
        .create(body=body, fields="id, name", supportsAllDrives=True)
        .execute(num_retries=5)
    )


def copy_file(service: Any, file_id: str, name: str, parent_id: str) -> dict:
    """
    Copy a file (including Google Docs types) into the destination parent.
    """
    body = {"name": name, "parents": [parent_id]}
    return (
        service.files()
        .copy(fileId=file_id, body=body, fields="id, name", supportsAllDrives=True)
        .execute(num_retries=5)
    )


def copy_folder_recursive(
    service: Any,
    src_folder_id: str,
    dst_parent_id: str,
    new_name: str | None = None,
    include_trashed: bool = False,
    dry_run: bool = False,
) -> tuple[str, str]:
    """
    Recursively copy a source folder (by ID) into a destination parent folder (by ID).
    Returns (source_folder_name, created_root_folder_id).
    """
    src_meta = get_file_metadata(service, src_folder_id)
    if not is_folder(src_meta):
        raise ValueError(f"Source ID '{src_folder_id}' is not a folder.")

    dst_parent_meta = get_file_metadata(service, dst_parent_id)
    if not is_folder(dst_parent_meta):
        raise ValueError(f"Destination parent ID '{dst_parent_id}' is not a folder.")

    src_name = src_meta["name"]
    root_name = new_name if new_name else src_name

    print(f"[plan] copy folder '{src_name}' ({src_folder_id}) -> parent '{dst_parent_meta['name']}' ({dst_parent_id}) as '{root_name}'")
    if dry_run:
        print("[dry-run] Skipping creation and file copies.")
        return src_name, "DRY_RUN"

    root_folder = create_folder(service, root_name, dst_parent_id)
    root_id = root_folder["id"]
    print(f"[create] folder '{root_name}' -> id: {root_id}")

    _copy_children_recursive(
        service=service,
        src_folder_id=src_folder_id,
        dst_folder_id=root_id,
        include_trashed=include_trashed,
    )

    return src_name, root_id


def _copy_children_recursive(
    service: Any,
    src_folder_id: str,
    dst_folder_id: str,
    include_trashed: bool,
) -> None:
    children = list_children(service, src_folder_id, include_trashed=include_trashed)
    for child in children:
        child_id = child["id"]
        child_name = child["name"]
        child_mime = child.get("mimeType", "")
        if child_mime == FOLDER_MIME_TYPE:
            print(f"[create] subfolder '{child_name}' in {dst_folder_id}")
            new_folder = create_folder(service, child_name, dst_folder_id)
            _copy_children_recursive(
                service=service,
                src_folder_id=child_id,
                dst_folder_id=new_folder["id"],
                include_trashed=include_trashed,
            )
        else:
            try:
                copied = copy_file(service, child_id, child_name, dst_folder_id)
                print(f"[copy] file '{child_name}' -> id: {copied['id']}")
            except Exception as err:
                # Continue copying other files if one fails
                print(f"[warn] failed to copy '{child_name}' ({child_id}): {err}", file=sys.stderr)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Copy a Google Drive folder (and its contents) to another location."
    )
    _ = parser.add_argument(
        "--src-id",
        required=True,
        help="Source folder ID to copy.",
    )
    _ = parser.add_argument(
        "--dst-id",
        required=True,
        help="Destination parent folder ID where the copy will be created.",
    )
    _ = parser.add_argument(
        "--new-name",
        default=None,
        help="Optional new name for the copied root folder.",
    )
    _ = parser.add_argument(
        "--credentials",
        default="credentials.json",
        help="Path to OAuth client secrets JSON (default: credentials.json).",
    )
    _ = parser.add_argument(
        "--token",
        default="token.json",
        help="Path to token cache JSON (default: token.json).",
    )
    _ = parser.add_argument(
        "--include-trashed",
        action="store_true",
        help="Include items in Trash from the source folder (default: false).",
    )
    _ = parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Plan and print actions without creating anything.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        service = build_drive_service(args.credentials, args.token)
        src_name, new_root_id = copy_folder_recursive(
            service=service,
            src_folder_id=args.src_id,
            dst_parent_id=args.dst_id,
            new_name=args.new_name,
            include_trashed=args.include_trashed,
            dry_run=args.dry_run,
        )
        if not args.dry_run:
            print(f"[done] '{src_name}' copied. New root folder id: {new_root_id}")
        return 0
    except Exception as exc:
        print(f"[error] {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())


