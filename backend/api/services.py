import os
import datetime
import re
import pytz
from django.conf import settings

# Ensure data directory exists
os.makedirs(settings.DATA_DIR, exist_ok=True)

# Create files if they don't exist
def ensure_files_exist():
    files = [
        settings.IP_BLOCKLIST_FILE,
        settings.DOMAIN_BLOCKLIST_FILE,
        settings.URL_BLOCKLIST_FILE,
        settings.LOG_FILE
    ]
    for file_path in files:
        if not os.path.exists(file_path):
            with open(file_path, 'w') as f:
                pass  # Create empty file

# Call this function when the module is imported
ensure_files_exist()

def sanitize_indicator(indicator):
    """Sanitize indicator by removing brackets, braces, and parentheses"""
    if not indicator:
        return ""
    
    # Process the indicator character by character
    result = ""
    i = 0
    while i < len(indicator):
        char = indicator[i]
        
        # Handle opening brackets/braces/parentheses
        if char in "[{(":
            # Look for the closing bracket/brace/parenthesis
            opening_char = char
            closing_char = "]" if char == "[" else "}" if char == "{" else ")"
            content_start = i + 1
            nesting_level = 1
            j = content_start
            
            # Find the matching closing bracket/brace/parenthesis
            while j < len(indicator) and nesting_level > 0:
                if indicator[j] == opening_char:
                    nesting_level += 1
                elif indicator[j] == closing_char:
                    nesting_level -= 1
                j += 1
            
            # If we found a matching closing bracket/brace/parenthesis
            if nesting_level == 0:
                content = indicator[content_start:j-1]
                # If the content is a dot, replace with a dot
                if content == ".":
                    result += "."
                # Otherwise, add the content directly
                else:
                    result += content
                i = j  # Skip to after the closing bracket/brace/parenthesis
            else:
                # No matching closing bracket/brace/parenthesis, treat as regular character
                result += char
                i += 1
        # Handle closing brackets/braces/parentheses without matching opening ones
        elif char in "]})": 
            # Skip these characters
            i += 1
        else:
            # Regular character
            result += char
            i += 1
    
    # Clean up any double dots that might have been created
    result = re.sub(r'\.+', '.', result)
    
    # Trim whitespace
    result = result.strip()
    
    return result

def validate_indicator_type(indicator_type, indicator):
    """Validate that the indicator matches the specified type"""
    # Basic validation patterns
    ip_pattern = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
    domain_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-\.]+)?\.[a-zA-Z]{2,}$'
    url_pattern = r'^https?://'
    
    if indicator_type == 'ip':
        return bool(re.match(ip_pattern, indicator))
    elif indicator_type == 'domain':
        return bool(re.match(domain_pattern, indicator)) and not bool(re.match(url_pattern, indicator))
    elif indicator_type == 'url':
        return bool(re.match(url_pattern, indicator))
    
    return False

def get_blocklist_file_path(indicator_type):
    """Return the appropriate file path based on indicator type"""
    if indicator_type == 'ip':
        return settings.IP_BLOCKLIST_FILE
    elif indicator_type == 'domain':
        return settings.DOMAIN_BLOCKLIST_FILE
    elif indicator_type == 'url':
        return settings.URL_BLOCKLIST_FILE
    else:
        raise ValueError(f"Unknown indicator type: {indicator_type}")

def read_blocklist(indicator_type):
    """Read the contents of a blocklist file"""
    file_path = get_blocklist_file_path(indicator_type)
    try:
        with open(file_path, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return []

def read_all_blocklists():
    """Read all blocklists and return a combined list with type information"""
    result = []
    
    # Read IP addresses
    for ip in read_blocklist('ip'):
        result.append({'indicator': ip, 'type': 'ip'})
    
    # Read domains
    for domain in read_blocklist('domain'):
        result.append({'indicator': domain, 'type': 'domain'})
    
    # Read URLs
    for url in read_blocklist('url'):
        result.append({'indicator': url, 'type': 'url'})
    
    return result

def add_to_blocklist(indicator_type, indicators, username, reason):
    """Add indicators to the appropriate blocklist file"""
    file_path = get_blocklist_file_path(indicator_type)
    
    # Get existing indicators to avoid duplicates
    existing_indicators = read_blocklist(indicator_type)
    
    # Process and validate indicators
    processed_indicators = []
    invalid_indicators = []
    existing_in_request = []
    
    for indicator in indicators:
        # Sanitize the indicator
        sanitized = sanitize_indicator(indicator)
        
        # Skip empty indicators
        if not sanitized:
            continue
        
        # Check if indicator already exists in the blocklist
        if sanitized in existing_indicators:
            existing_in_request.append(sanitized)
            continue
        
        # Validate indicator type
        if validate_indicator_type(indicator_type, sanitized):
            processed_indicators.append(sanitized)
        else:
            invalid_indicators.append({
                'original': indicator,
                'sanitized': sanitized,
                'reason': f'Not a valid {indicator_type}'
            })
    
    # Filter out indicators that already exist
    new_indicators = [ind for ind in processed_indicators if ind not in existing_indicators]
    
    # If there are new indicators to add
    if new_indicators:
        with open(file_path, 'a') as f:
            for indicator in new_indicators:
                f.write(f"{indicator}\n")
        
        # Log the action
        log_action(username, 'BLOCK', indicator_type, new_indicators, reason)
    
    return {
        'added': new_indicators,
        'invalid': invalid_indicators,
        'existing': existing_in_request
    }

def remove_from_blocklist(indicator_type, indicators, username, reason):
    """Remove indicators from the appropriate blocklist file"""
    file_path = get_blocklist_file_path(indicator_type)
    
    # Get existing indicators
    existing_indicators = read_blocklist(indicator_type)
    
    # Process indicators
    processed_indicators = [sanitize_indicator(ind) for ind in indicators if sanitize_indicator(ind)]
    
    # Filter indicators that exist and can be removed
    removable_indicators = [ind for ind in processed_indicators if ind in existing_indicators]
    
    # Identify indicators that don't exist in the blocklist
    non_existent = [ind for ind in processed_indicators if ind not in existing_indicators]
    
    # If there are indicators to remove
    if removable_indicators:
        # Create a new list without the indicators to remove
        updated_indicators = [ind for ind in existing_indicators if ind not in removable_indicators]
        
        # Write the updated list back to the file
        with open(file_path, 'w') as f:
            for indicator in updated_indicators:
                f.write(f"{indicator}\n")
        
        # Log the action
        log_action(username, 'UNBLOCK', indicator_type, removable_indicators, reason)
    
    return {
        'removed': removable_indicators,
        'non_existent': non_existent
    }

def log_action(username, action, indicator_type, indicators, reason):
    """Log an action to the log file"""
    # Get current time in GMT+3
    tz = pytz.timezone('Europe/Istanbul')  # Istanbul is GMT+3
    timestamp = datetime.datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S %z")
    
    with open(settings.LOG_FILE, 'a') as f:
        for indicator in indicators:
            log_entry = f"{timestamp} | {username} | {action} | {indicator_type} | {indicator} | {reason}\n"
            f.write(log_entry)

def read_logs(limit=None):
    """Read the log file and return entries"""
    try:
        with open(settings.LOG_FILE, 'r') as f:
            logs = [line.strip() for line in f if line.strip()]
            
        # Parse log entries into structured format
        parsed_logs = []
        for log in logs:
            parts = log.split(' | ')
            if len(parts) >= 6:
                parsed_logs.append({
                    'timestamp': parts[0],
                    'username': parts[1],
                    'action': parts[2],
                    'indicator_type': parts[3],  
                    'indicator': parts[4],
                    'reason': parts[5]
                })
        
        # Sort logs by timestamp in descending order (newest first)
        parsed_logs.sort(key=lambda x: x['timestamp'], reverse=True)
        
        # Return limited number of logs if specified
        if limit and isinstance(limit, int):
            return parsed_logs[:limit]
        return parsed_logs
    except FileNotFoundError:
        return []

def get_logs(limit=None):
    """Get logs for the API - wrapper around read_logs with error handling"""
    try:
        return read_logs(limit)
    except Exception as e:
        # Return an empty list on error
        print(f"Error reading logs: {str(e)}")
        return []
