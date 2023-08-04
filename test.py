import re

def extract_part_from_url(url, position=0):
    # Regular expression pattern to find the desired part
    pattern = r'([^/]+)'

    # Extract all parts separated by "/"
    parts = re.findall(pattern, url)

    # Return the part at the specified position (default: 0)
    return parts[position]

# Example URL
url = "https://office.homura.top:82/cache/files/new.docx3Fsign3Did_7188/output.docx/output.docx?md5=bSncuDb8dptNoXggcJ9ygQ&expires=1691038933&filename=output.docx"

# Extract the desired part at position 1
desired_part = extract_part_from_url(url, 4)
print(desired_part)  # Output: new.docx3Fsign3Did_7188
