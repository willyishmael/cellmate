
from datetime import datetime, date
from openpyxl.utils.datetime import from_excel
import re


def format_date(self, value) -> str:
        """Ensure date formatted as yyyy-mm-dd string.

        Handles:
        - datetime objects
        - ISO-like 'YYYY-MM-DD' or 'YYYY/MM/DD'
        - 'DD/MM/YYYY' and 'DD-MM-YYYY'
        - 'DD/MM' (no year) -> assumes current year

        Falls back to returning the original string if parsing fails.
        """
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d")

        s = str(value).strip()

        # Common full-date formats
        for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%d/%m/%Y", "%d-%m-%Y"):
            try:
                return datetime.strptime(s, fmt).strftime("%Y-%m-%d")
            except Exception:
                pass

        # Handle day-month with abbreviated or full month name, e.g. '26-Oct-2025' or '26-October-2025'
        for fmt in ("%d-%b-%Y", "%d-%B-%Y", "%d %b %Y", "%d %B %Y"):
            try:
                return datetime.strptime(s, fmt).strftime("%Y-%m-%d")
            except Exception:
                pass

        # Handle day/month without year, e.g. '08/10' -> assume current year
        try:
            if re.match(r"^\d{1,2}/\d{1,2}$", s):
                day_str, month_str = s.split("/")
                year = datetime.now().year
                dt = datetime(year=year, month=int(month_str), day=int(day_str))
                return dt.strftime("%Y-%m-%d")
        except Exception:
            pass

        # Fallback: return original string
        return s
    
def try_parse_date(self, value, default_year: int | None = None) -> date | None:
        """Try to parse a cell value into a datetime.date.

        Returns a datetime.date on success, or None when parsing fails.
        default_year: if provided, used when parsing day/month values without a year.
        """
        # Only accept native date/datetime, Excel serials, or strings in 'YYYY-MM-DD'.
        if value is None:
            return None

        if isinstance(value, datetime):
            return value.date()

        if isinstance(value, date):
            return value

        s = str(value).strip()
        if not s:
            return None

        try:
            # numeric cell value
            if isinstance(value, (int, float)):
                return from_excel(float(value)).date()
            # numeric string
            if s.replace('.', '', 1).isdigit():
                return from_excel(float(s)).date()
        except Exception:
            pass

        # Expect string in 'YYYY-MM-DD' exactly
        try:
            parsed = datetime.strptime(s, "%Y-%m-%d")
            return parsed.date()
        except Exception:
            return None