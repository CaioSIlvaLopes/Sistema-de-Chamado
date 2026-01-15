from django.utils import timezone
import datetime

# Business hours configuration
BUSINESS_START_HOUR = 9
BUSINESS_END_HOUR = 18

def is_business_hours(dt: datetime.datetime) -> bool:
    """Check if a datetime is within business hours (Mon-Fri, 9-18)."""
    if dt.weekday() >= 5:  # Saturday or Sunday
        return False
    return BUSINESS_START_HOUR <= dt.hour < BUSINESS_END_HOUR

def get_next_business_start(dt: datetime.datetime) -> datetime.datetime:
    """Move datetime to the next business start time."""
    # Logic to move to next valid slot
    
    # If currently within business hours? No, this function assumes we need to move.
    # We'll just iterate until we find a valid start.
    
    current = dt
    
    # If we are post-business hours on a weekday, move to next day
    if current.hour >= BUSINESS_END_HOUR and current.weekday() < 5:
        current = current + datetime.timedelta(days=1)
        current = current.replace(hour=BUSINESS_START_HOUR, minute=0, second=0, microsecond=0)
    
    # If we are pre-business hours on a weekday, move to 9am
    elif current.hour < BUSINESS_START_HOUR and current.weekday() < 5:
        current = current.replace(hour=BUSINESS_START_HOUR, minute=0, second=0, microsecond=0)
        
    # Whilst it is a weekend or still not a weekday (loop to be safe)
    while current.weekday() >= 5: # 5=Sat, 6=Sun
        current = current + datetime.timedelta(days=1)
        current = current.replace(hour=BUSINESS_START_HOUR, minute=0, second=0, microsecond=0)
        
    return current

def calculate_due_date(start_date: datetime.datetime, hours_to_add: int) -> datetime.datetime:
    """
    Calculate due date adding business hours only.
    start_date: aware datetime
    hours_to_add: integer hours
    """
    if not timezone.is_aware(start_date):
        start_date = timezone.make_aware(start_date)
        
    current_time = start_date
    remaining_minutes = hours_to_add * 60
    
    # First, ensure we start counting from a valid business moment
    # If started at Friday 19:00, we effectively start counting from Monday 09:00
    if not is_business_hours(current_time):
        current_time = get_next_business_start(current_time)
        
    while remaining_minutes > 0:
        # Determine end of current business day
        # It is always today at 18:00 because get_next_business_start ensures we are inside a day or at start of one
        today_end = current_time.replace(hour=BUSINESS_END_HOUR, minute=0, second=0, microsecond=0)
        
        # Calculate minutes left in this day
        minutes_left_today = int((today_end - current_time).total_seconds() / 60)
        
        if minutes_left_today > remaining_minutes:
            # We can fit the remaining time in today
            current_time += datetime.timedelta(minutes=remaining_minutes)
            remaining_minutes = 0
        else:
            # We use up the rest of today
            remaining_minutes -= minutes_left_today
            # Move to next business slot (tomorrow 9am or monday 9am)
            current_time = today_end # We are effectively at 18:00
            current_time = get_next_business_start(current_time)
            
    return current_time

def get_business_time_left(start_date: datetime.datetime, end_date: datetime.datetime) -> int:
    """
    Calculate remaining business seconds between start_date (now) and end_date (due).
    Returns 0 if start_date >= end_date.
    """
    if start_date >= end_date:
        return 0
        
    if not timezone.is_aware(start_date):
        start_date = timezone.make_aware(start_date)
    if not timezone.is_aware(end_date):
        end_date = timezone.make_aware(end_date)
        
    total_seconds = 0
    current = start_date
    
    # Iterate day by day or hour by hour?
    # Simple iteration: Jump to next boundary.
    
    while current < end_date:
        # If current is outside business hours, jump to next start
        if not is_business_hours(current):
            current = get_next_business_start(current)
            if current >= end_date:
                break
                
        # Now we are inside business hours (or at the exact start of one)
        # The segment ends at either:
        # 1. The end of this business day (18:00)
        # 2. The end_date itself
        
        today_end = current.replace(hour=BUSINESS_END_HOUR, minute=0, second=0, microsecond=0)
        
        segment_end = min(today_end, end_date)
        
        diff = (segment_end - current).total_seconds()
        if diff > 0:
            total_seconds += diff
            
        current = segment_end
        
        # If we reached today_end, we might need to jump to next day
        # If we reached end_date, loop will terminate
        
    return int(total_seconds)
