import requests #requests==2.26.0
import json
from bs4 import BeautifulSoup #beautifulsoup4==4.10.0 
import os, sys

#기본 웹 사항 확인하는 함수
def get_web_content(url):
    return BeautifulSoup(requests.get(url).content,"html.parser")
def get_web_headers(url):
    return requests.get(url).headers

#말그대로 insta를 파싱해주는 것
def insta_PARSE() -> list:
  soup = get_web_content("https://www.picuki.com/profile/mju_betterwe")
  div = soup.find("div",{"class": "content box-photos-wrapper"})
  d = div.find_all(lambda x: x.name=="a" and x.attrs.get("href"))
  d_dictlist = []
  for _ in d:
      if _.img != None:
          d_dict = _.img.attrs
          d_dict["pubtime"] = _.parent.parent.find("div",class_="time").span. get_text()
          d_dictlist.append(d_dict)
  return d_dictlist


#공지형식의 임베드 구조 만들고 포스트 하기
def POST_insta(dictlist, webhook_url):
  data = {
  "content": "",
  "embeds": [
    {
      "description": dictlist["alt"],
      "color": 5814783,
      "author": {
        "name": "@mju_betterwe",
        "url": "https://www.instagram.com/mju_betterwe/"
      },
      "footer": {
        "text": dictlist["pubtime"]
      },
      "image": {
        "url": dictlist['src']
      }
    }
  ]
}
  #post request
  requests.post(
    webhook_url,
    data=json.dumps(data),
    headers={'Content-Type' : 'application/json'})

#instas는 insta들(복수 s)라는 뜻이다.
  
def main():
  print(os.getcwd())
  recent_path = "./recent.json"
  
  instas = insta_PARSE()
  beforeinstas = instas
  beforelen = len(instas)
  print("before instas length:", beforelen) 
  
  if os.path.isfile(recent_path):
    recent = open(recent_path, "r", encoding="utf-8").readlines()
    try: recent = json.loads("\n".join(recent))
    except Exception as e: return print(f"JSON Loading Error:\n{e}")

    #제목과 summary가 같으면 instas 업데이트 후 break
    for i, insta in enumerate(instas): 
      if recent["alt"] == insta["alt"]:
        if i == 0: instas = []
        else: instas = instas[i-1::-1]
        print("'i' when for ended':", i)
        print("break")
        break
  else:
    instas = (instas[0],)
  
  
  #확인용 출력
  print("after instas length:", len(instas))
  #정상적으로 필터링이 된 경우
  if len(instas) > 0 and len(instas) < beforelen:
    #확인용 출력
    print("instas[0]['alt']:", instas[0]['alt'])
    print("instas[0]['src']:", instas[0]['src'])
    #웹후크 주소로 보내기
    for webhook_url in sys.argv[1:]:
      for insta in instas:
        POST_insta(insta, webhook_url)

  elif len(instas) == 0:
    print("There is nothing to send.")
  
  #정상적으로 필터링이 안된경우
  elif beforelen <= len(instas): 
    print("Error but pass over: recent.json과 동일한 내용의 insta 포스트가 포착되지 않았습니다. ")
    instas = (beforeinstas[0],)
  
  else:
    print("Unknown Error")
    return #프로그램 종료

  #instas가 비어있지 않아야만 파일을 새로 씀.
  if len(instas) > 0:
    with open(recent_path, "w", encoding="utf-8") as w:
      w.write(json.dumps(instas[-1]))
      w.close()
  else:
    print("Nothing was written.")
    

if __name__ == '__main__':
    main()
