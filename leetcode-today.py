# coding=<encoding name> ： # coding=utf-8
import requests
import json
import smtplib
import os
from email.mime.text import MIMEText

base_url = 'https://leetcode.cn'

# 获取今天的每日一题名称
response = requests.post(base_url + "/graphql", json={
    "query": "query questionOfToday {  todayRecord {    date    userStatus    question {      questionId      frontendQuestionId: questionFrontendId      difficulty      title      titleCn: translatedTitle      titleSlug      paidOnly: isPaidOnly      freqBar      isFavor      acRate      status      solutionNum      hasVideoSolution      topicTags {        name        nameTranslated: translatedName        id      }      extra {        topCompanyTags {          imgUrl          slug          numSubscribed        }      }    }    lastSubmission {      id    }  }}    ",
    "variables": {}
})
question_name_english = json.loads(response.text).get('data').get('todayRecord')[0].get("question").get('titleSlug')
# 获取今日每日一题的所有信息
url = base_url + "/problems/" + question_name_english
response = requests.post(base_url + "/graphql",
                         json={"operationName": "questionData", "variables": {"titleSlug": question_name_english},
                               "query": "query questionData($titleSlug: String!) {  question(titleSlug: $titleSlug) {    questionId    questionFrontendId    boundTopicId    title    titleSlug    content    translatedTitle    translatedContent    isPaidOnly    difficulty    likes    dislikes    isLiked    similarQuestions    contributors {      username      profileUrl      avatarUrl      __typename    }    langToValidPlayground    topicTags {      name      slug      translatedName      __typename    }    companyTagStats    codeSnippets {      lang      langSlug      code      __typename    }    stats    hints    solution {      id      canSeeDetail      __typename    }    status    sampleTestCase    metaData    judgerAvailable    judgeType    mysqlSchemas    enableRunCode    envInfo    book {      id      bookName      pressName      source      shortDescription      fullDescription      bookImgUrl      pressImgUrl      productUrl      __typename    }    isSubscribed    isDailyQuestion    dailyRecordStatus    editorType    ugcQuestionId    style    __typename  }}"})
# 转化成json格式
question_info = json.loads(response.text).get('data').get("question")
# 题目题号
question_frontend_id = question_info.get('questionFrontendId')
# 题目中文名称
question_name_chinese = question_info.get('translatedTitle')
# 题目难度
question_difficulty = question_info.get('difficulty')
# 题目内容
question_content = question_info.get('translatedContent')
# 把第一个答案拿出来
response = requests.post(base_url + "/graphql",
                         json={
    "operationName": "questionSolutionArticles",
    "variables": {
        "questionSlug": question_name_english,
        "first": 10,
        "skip": 0,
        "orderBy": "DEFAULT"
    },
    "query": "query questionSolutionArticles($questionSlug: String!, $skip: Int, $first: Int, $orderBy: SolutionArticleOrderBy, $userInput: String, $tagSlugs: [String!]) {  questionSolutionArticles(questionSlug: $questionSlug, skip: $skip, first: $first, orderBy: $orderBy, userInput: $userInput, tagSlugs: $tagSlugs) {    totalNum    edges {      node {        ...solutionArticle        __typename      }      __typename    }    __typename  }}fragment solutionArticle on SolutionArticleNode {  rewardEnabled  canEditReward  uuid  title  slug  sunk  chargeType  status  identifier  canEdit  canSee  reactionType  reactionsV2 {    count    reactionType    __typename  }  tags {    name    nameTranslated    slug    tagType    __typename  }  createdAt  thumbnail  author {    username    profile {      userAvatar      userSlug      realName      __typename    }    __typename  }  summary  topic {    id    commentCount    viewCount    __typename  }  byLeetcode  isMyFavorite  isMostPopular  isEditorsPick  hitCount  videosInfo {    videoId    coverUrl    duration    __typename  }  __typename}"
    })
answer_name_english = json.loads(response.text).get('data').get('questionSolutionArticles').get('edges')[0].get('node').get('slug')
# 第一个答案的内容
response = requests.post(base_url + "/graphql",
                         json={
    "operationName": "solutionDetailArticle",
    "variables": {
        "slug": answer_name_english,
        "orderBy": "DEFAULT"
    },
    "query": "query solutionDetailArticle($slug: String!, $orderBy: SolutionArticleOrderBy!) {\n  solutionArticle(slug: $slug, orderBy: $orderBy) {\n    ...solutionArticle\n    content\n    question {\n      questionTitleSlug\n      __typename\n    }\n    position\n    next {\n      slug\n      title\n      __typename\n    }\n    prev {\n      slug\n      title\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment solutionArticle on SolutionArticleNode {\n  rewardEnabled\n  canEditReward\n  uuid\n  title\n  slug\n  sunk\n  chargeType\n  status\n  identifier\n  canEdit\n  canSee\n  reactionType\n  reactionsV2 {\n    count\n    reactionType\n    __typename\n  }\n  tags {\n    name\n    nameTranslated\n    slug\n    tagType\n    __typename\n  }\n  createdAt\n  thumbnail\n  author {\n    username\n    profile {\n      userAvatar\n      userSlug\n      realName\n      __typename\n    }\n    __typename\n  }\n  summary\n  topic {\n    id\n    commentCount\n    viewCount\n    __typename\n  }\n  byLeetcode\n  isMyFavorite\n  isMostPopular\n  isEditorsPick\n  hitCount\n  videosInfo {\n    videoId\n    coverUrl\n    duration\n    __typename\n  }\n  __typename\n}\n"
})
answer_content = json.loads(response.text).get('data').get('solutionArticle').get('content')
java_answer =  answer_content.split('```Java [sol1-Java]')[1].split('```')[0]
java_answer_html = '<pre class="brush: java;">\n' + java_answer + '\n</pre>'
htmlText = """ <head>
        <meta charset=UTF-8>
        <link rel="stylesheet">
        <style>
            code {
                color: blue;
                font-size: larger;
            }
        </style>
        </link>
    </head>
    <body>
<div>
    """ + question_content + '本题连接：<a href=' + url + ">" + url + "</a></div>"+ """<div>
<p>
<strong>Java 答案：</strong>
</p>
<div>""" + java_answer_html + """</div>
</div>
"""
# 获取 GitHub workflow 的变量
send_username = os.environ["send_username"]
send_authroization = os.environ["send_authroization"]
receive_user_1 = os.environ["receive_user_1"]
receive_user_2 = os.environ["receive_user_2"]
# 邮箱类
class Email:
    def __init__(self, sender_name, sender_address, email_host, email_port, authroization, receive_user_list, title, message):
        self.sender_name = sender_name
        self.sender_address = sender_address
        self.email_host = email_host
        self.email_port = email_port
        self.authroization = authroization
        self.receive_user_list = receive_user_list
        self.message = message
        self.title = title
       
    def send_email(self):
        try:
            user = self.sender_name + "<" + self.sender_address + ">"
            message = MIMEText(self.message, _subtype='html', _charset='utf-8')
            message['Subject'] = self.title
            message['From'] = user
            message['To'] = ";".join(self.receive_user_list)
            server = smtplib.SMTP_SSL(self.email_host)
            server.connect(self.email_host, self.email_port)
            server.login(self.sender_address, self.authroization)
            server.sendmail(user, self.receive_user_list, message.as_string())
            server.close()
            print("success!!!")
        except Exception as e:
            print("error:", e)
            
if __name__ == '__main__':
    # 邮件上显示的昵称
    sender_name = "LeetCode 每日一题自动推送"
    # 发件人邮箱
    sender_address = send_username
    # 邮箱对应的host
    email_host = "smtp.163.com"
    email_port = 465
    # SMTP 授权
    authroization = send_authroization
    # 收件人邮箱账户列表
    receive_user_list = [receive_user_1, receive_user_2]
    # 邮件标题
    title = question_frontend_id + '.' + question_name_chinese + '.' + question_difficulty
    message = htmlText
    email = Email(sender_name, sender_address, email_host, email_port, authroization, receive_user_list, title, message)
    email.send_email()
