import requests

def check_links(file_path):
    # Read all links from the file
    with open(file_path, 'r') as file:
        links = file.readlines()

    working_links = []
    cnt = 0
    # Check each link
    for link in links:
        link = link.strip()  # Remove any leading/trailing whitespace
        try:
            response = requests.head(link, timeout=5)
            if response.status_code < 400:
                working_links.append(link)
            else:
                print(f"Broken link: {link}")
        except requests.RequestException:
            print(f"Failed to connect: {link}")
        cnt += 1
        print(cnt)

    # Write back only the working links
    with open(file_path, 'w') as file:
        file.write("\n".join(working_links))
    

if __name__ == "__main__":
    file_path = "links.txt"  # Path to the links file
    check_links(file_path)