import streamlit as st
import os
from openai import OpenAI
import json
from datetime import datetime



# 模板
st.set_page_config(
    page_title="AI智能伴侣",
    page_icon="💖",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.baidu.com',
        'Report a bug': "https://www.github.com",
        'About': "# 这是一个ptf的ai助手"
    }
)
#保存对话信息的函数
def save_session():
    # 保存当前对话
    if "current_session" in st.session_state:
        session_date = {
            "nick_name": st.session_state.nick_name,
            "nature": st.session_state.nature,
            "current_session": st.session_state.current_session,
            "messages": st.session_state.messages
        }
    # 如果sessions目录不存在则创建
    if not os.path.exists("sessions"):
        os.mkdir("sessions")
    with open(f"sessions/{st.session_state.current_session}.json", "w", encoding="utf-8") as f:
        json.dump(session_date, f, ensure_ascii=False, indent=4)

# 拿取sessions的文件
def get_sessions():
    session_list = []
    if os.path.exists("sessions"):
        for file in os.listdir("sessions"):
            if file.endswith(".json"):
                    session_list.append(file[:-5])
    session_list.sort(reverse=True)
    return session_list

# 获取历史对话
def load_session(session_name):
    session_date = {}
    if os.path.exists(f"sessions/{session_name}.json"):
        with open(f"sessions/{session_name}.json","r",encoding="utf-8") as f:
            session_date = json.load(f)
            st.session_state.nick_name = session_date["nick_name"]
            st.session_state.nature = session_date["nature"]
            st.session_state.messages = session_date["messages"]
            st.session_state.current_session = session_date["current_session"]

# 删除对话
def delete_session(session_name):
    if os.path.exists(f"sessions/{session_name}.json"):
        os.remove(f"sessions/{session_name}.json")
        if st.session_state.current_session == session_name:
            st.session_state.messages = []
            st.session_state.current_session = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

def exit_nonesession(session_name):
    for file in os.listdir(f"{session_name}"):
        if file.endswith(".json"):
            with open(f"{session_name}/{file}", "r", encoding="utf-8") as f:
                session_date = json.load(f)
                if not session_date["messages"]:
                    st.session_state.nick_name = session_date["nick_name"]
                    st.session_state.nature = session_date["nature"]
                    st.session_state.messages = session_date["messages"]
                    st.session_state.current_session = session_date["current_session"]

#大标题
st.title("AI智能伴侣")
st.logo("logo.png")
system_prompt = """现在你是用户的真实伴侣，你的名字叫%s，请完全带入伴侣角色，请不要使用删除线格式。
            规则:
                1.每次只回一条消息
                2.匹配用户的语言
                3.回复简短，像微信聊天一样
                4.有需要可以用符号表情或者emoji
                5.用符合伴侣性格的方式回复
                
            伴侣性格:
                --%s
                
            你必须严格遵守上述规则回复用户
                """



print("-------->重新渲染")
# 初始化性格 名字
if "nick_name" not in st.session_state:
    st.session_state.nick_name = "小慕慕"

if "nature" not in st.session_state:
    st.session_state.nature = "活泼温柔可爱"

#初始化聊天记录
if "messages" not in st.session_state:
    if os.path.exists("sessions"):
        exit_nonesession("sessions")
    if "messages" not in st.session_state:
        st.session_state.messages = []

# 保存对话信息
if "current_session" not in st.session_state:
    st.session_state.current_session = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


# 侧边栏
with st.sidebar:
    st.subheader("AI控制面板")
    #新建聊天
    if st.button("新建聊天",width="stretch",icon="🖋️"):
        # 重置messages,current_session并保存
        if os.path.exists("sessions"):
            exit_nonesession("sessions")
        if st.session_state.messages :
            st.session_state.messages = []
            st.session_state.current_session = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            save_session()

    session_list = get_sessions()
    if session_list:
        for session in session_list:
            col1,col2 = st.columns([4,1])
            with col1:
                if st.button(session,width="stretch",icon="💬",key=f"load_{session}",type="primary" if st.session_state.current_session == session else "secondary"):
                    load_session(session)
                    st.rerun()
            with col2:
                if st.button("",width="stretch",icon="❌",key=f"delete_{session}"):
                    delete_session(session)
                    st.rerun()

    # 分隔线
    st.divider()

    # 伴侣信息
    st.subheader("伴侣信息")
    nick_name = st.text_input("昵称",placeholder="请输入昵称",value=st.session_state.nick_name)
    if nick_name:
        st.session_state.nick_name = nick_name

    nature = st.text_area("性格",placeholder="请输入性格",value=st.session_state.nature)
    if nature:
        st.session_state.nature = nature


#输出保存的对话
for message in st.session_state.messages:
    st.chat_message(message["role"]).write(message["content"])


# 调用deepseek
client = OpenAI(  api_key=os.environ.get('DEEPSEEK_API_KEY'), base_url="https://api.deepseek.com")

prompt = st.chat_input("请输入内容")
if prompt :
    st.session_state.messages.append({"role": "user", "content": prompt})

    print([{"role": "system","content": system_prompt},*st.session_state.messages])

    st.chat_message("user").write(prompt)
    print(f"------->",prompt)
    response = client.chat.completions.create(
        model="deepseek-v4-flash",
        messages=[
            {"role": "system","content": system_prompt % (st.session_state.nick_name,st.session_state.nature)},
            *st.session_state.messages
        ],
        stream=True,

    )


    # 非流式输出
    # print(f"<---------",response.choices[0].message.content)
    # st.chat_message("assistant").write(response.choices[0].message.content)
    # st.session_state.messages.append({"role": "assistant", "content": response.choices[0].message.content})

    #流式输出
    response_message = st.empty()
    zifuchuan = ""
    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            content = chunk.choices[0].delta.content
            zifuchuan += content
            response_message.chat_message("assistant").write(zifuchuan)


    st.session_state.messages.append({"role": "assistant", "content": zifuchuan})
    save_session()


print("===============")

