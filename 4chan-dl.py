import requests
from bs4 import BeautifulSoup
from rich import print
from rich.progress import track
import multiprocessing
from pick import pick

def main():
    chan = input("Enter the channel name: ")
    url = f"https://boards.4channel.org/{chan}/"
    threads = []

    for i in track(range(1, 11), description="Fetching Sites"):
        page_url = url + ("" if i == 1 else str(i))
        threads.extend(get_threads(page_url))

    subjects = get_subjects(threads)

    _, index = pick(subjects, "Which Thread do you want to download?")

    thread = threads[index]
    img_urls = get_image_urls(thread, url)

    with multiprocessing.Pool() as pool:
        pool.map(download_image, ["https:" + img_url for img_url in img_urls])

    print("Done!")

def get_soup(url):
    html = requests.get(url).content
    soup = BeautifulSoup(html, 'html.parser')
    print(f"got html of: {url}")
    return soup

def get_threads(url):
    soup = get_soup(url)
    return soup.find_all('div', class_='thread')

def get_subjects(threads):
    subjects = []
    for thread in threads:
        subject = thread.find('span', class_='subject')
        if subject:
            subjects.append(subject.text)
    return subjects

def get_image_urls(thread, url):
    all_images = []

    site = thread.find('a', class_='replylink')['href']
    soup = get_soup(url + "/" + site)
    imgs = soup.find_all('a', class_='fileThumb')
    if imgs:
        for img in imgs:
            all_images.append(img.get('href'))
    return all_images

def download_image(img_url):
    img = requests.get(img_url)
    if img.status_code == 200:
        img_name = img_url.split('/')[-1]
        with open(img_name, 'wb') as f:
            f.write(img.content)
        print('Image successfully Downloaded:', img_name)
    else:
        print('Image Couldn\'t be retrieved')

if __name__ == '__main__':
    main()
