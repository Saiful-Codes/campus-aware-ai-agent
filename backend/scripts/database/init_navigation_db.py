import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from app.services.navigation_bootstrap_service import bootstrap_navigation_data


def main() -> None:
    locations_count, facilities_count, paths_count = bootstrap_navigation_data()
    print(
        "Navigation bootstrap complete: "
        f"locations={locations_count}, facilities={facilities_count}, paths={paths_count}"
    )


if __name__ == "__main__":
    main()
