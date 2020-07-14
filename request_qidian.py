import requests
import json
from bs4 import BeautifulSoup as soup

header = {'Cookie':'_qda_uuid=2d67cc38-20d9-bcf6-64ba-212f68994394; _csrfToken=qug6xFVggMPStXAwDn0Y9kSclJRxNS8zTBqKUsCY; newstatisticUUID=1594089986_927969374; e1=%7B%22pid%22%3A%22qd_P_Searchresult%22%2C%22eid%22%3A%22qd_S05%22%2C%22l1%22%3A3%7D; e2=%7B%22pid%22%3A%22qd_P_Searchresult%22%2C%22eid%22%3A%22%22%2C%22l1%22%3A2%7D; qdrs=0%7C3%7C0%7C0%7C1; showSectionCommentGuide=1; qdgd=1; lrbc=1010868264%7C402733549%7C0; rcr=1010868264; bc=1010868264; ywkey=ywkwFqbhV2AL; ywguid=854002289976; ywopenid=A0308F2BDB5684D367242DD7FA68CF7F',
              'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',
              'Accept-Language': 'zh-CN,zh;q=0.9'
              }
session = requests.session()
csrfToken = 'qug6xFVggMPStXAwDn0Y9kSclJRxNS8zTBqKUsCY'


def get_chapter_ids(book_id = 0):
    res = session.get(
        "https://book.qidian.com/ajax/book/category?_csrfToken={}&bookId={}".format(csrfToken, book_id),
        headers=header
    )
    if res.status_code != 200:
        print('http error, status: {}'.format(res.status_code))
        return []
    category = json.loads(res.content.decode())
    if category['code'] != 0:
        print('request error, body: {}'.format(category))
        return []
    ids = map(lambda vs: map(lambda cs: [cs['id'], cs['cN']],vs['cs']), category['data']['vs'])
    return [i for p in ids for i in p]


def get_chapter(book_id = 0, chapter_id = 0):
    res = session.get('https://vipreader.qidian.com/chapter/{}/{}'.format(book_id, chapter_id), headers=header)
    if res.status_code != 200:
        print('http error, status: {}'.format(res.status_code))
        return []
    context = res.text
    html = soup(context, features="lxml")
    paragraphs = html.find_all('div', class_='read-content j_readContent')[0].contents
    return [i.text for i in paragraphs[1:]]


def get_reviews(book_id = 0, chapter_id = 0, segment_id=0):
    res = session.get(
        'https://read.qidian.com/ajax/chapterReview/reviewList?'
        '_csrfToken={}&bookId={}&chapterId={}&segmentId={}&type=2&page=1&pageSize=50'
            .format(csrfToken, book_id, chapter_id, segment_id),
        headers=header)
    if res.status_code != 200:
        print('http error, status: {}'.format
              (res.status_code))
        return []
    res = res.json()
    if res['code'] != 0:
        print('request error, body: {}'.format(res))
        return []
    reviews = res['data']['list']
    return [review['content'] for review in reviews]



if __name__=='__main__':
    ids = get_chapter_ids()
    paragraphs = get_chapter(chapter_id=ids[5][0])
    reviews = get_reviews(chapter_id=ids[5][0], segment_id=75)
    pass
