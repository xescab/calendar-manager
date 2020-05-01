import click
import json
import sys
from calendar_manager.read_gspread import get_all_cells_from_spreadsheet, read_month, get_event_templates, get_caregivers
from calendar_manager.event_scheduler import EventScheduler


@click.command()
@click.option('--settings-filename', '-f', default="settings.json", show_default=True,
    help="File containing settings such as calendar_id, spreadsheet_filename and spreadsheet_tab")
@click.option('--credentials-filename', '-c', default="creds.json", show_default=True,
    help="File containing the credentials necessary to access Google APIs")
@click.option('--month', '-m', default=None, help="Month for which to export events to Google calendar")
@click.option('--preview/--no-preview', default=True, show_default=True, help="Whether to preview events to be scheduled or not")
@click.option('--schedule/--no-schedule', default=False, show_default=True, help="Whether to actually schedule events on Google Calendar or not")
def cli(settings_filename, credentials_filename, month, preview, schedule):
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
    print(f"Spreadsheet tab:     \t{settings['spreadsheet_tab']}\n")

    print(f"Month to export:     \t{month}\n")

    # Read spreadsheet
    all_cells = get_all_cells_from_spreadsheet(credentials_filename, settings['spreadsheet_filename'], settings['spreadsheet_tab'])

    calendar_school_period = settings['spreadsheet_tab']
    month_data = read_month(all_cells, calendar_school_period, month)
    #print(json.dumps(month_data, sort_keys=True, indent=4))

    caregivers = get_caregivers(all_cells)
    event_templates = get_event_templates(all_cells)

    scheduler = EventScheduler(credentials_filename, settings['calendar_id'], settings['calendar_timezone'], event_templates, caregivers, month_data)

    if preview:
        scheduler.list_events_to_be_scheduled()

    if schedule:
        scheduler.schedule_events()
        
    scheduler.print_datetype_distribution()


if __name__ == '__main__':
    cli()