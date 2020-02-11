import click
import json
import sys
from create_events import schedule_events_from_spreadsheet

@click.command()
@click.option('--settings-filename', '-f', default="settings.json", 
    help="File containing settings such as calendar_id, spreadsheet_filename and spreadsheet_tab")
@click.option('--month', '-m', default=None, help="Month for which to export events to Google calendar")
def cli(settings_filename, month):
    settings_file = None
    if settings_filename:
        try:
            settings_file = open(settings_filename)
            settings = json.load(settings_file)
        except Exception:
            print(f"Could not open or read file {settings_filename}")
            sys.exit(1)
    else:
        raise click.UsageError("must pass settings filename")

    if not month:
        raise click.UsageError("must pass month for which to export events")

    print(f"=== Settings read from {settings_filename} ===")
    print(f"Calendar ID:         \t{settings['calendar_id']}")
    print(f"Calendar timezone:   \t{settings['calendar_timezone']}")
    print(f"Spreadsheet filename:\t{settings['spreadsheet_filename']}")
    print(f"Spreadsheet tab:     \t{settings['spreadsheet_tab']}")

    print(f"\nMonth to export:     \t{month}")

    schedule_events_from_spreadsheet(settings['spreadsheet_filename'], settings['spreadsheet_tab'], month)


if __name__ == '__main__':
    cli()