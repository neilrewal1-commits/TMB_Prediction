"""A six-chapter learning guide, available in both app views."""
import streamlit as st

from care_app.cancer_basics_content import CHAPTERS, SOURCES, SOURCES_CHECKED, reading_guide
from care_app.cancer_basics_diagrams import illustration

st.title('Cancer Basics')
st.write('Learn at your own pace: five chapters about cancer and a dedicated chapter about stomach cancer. Choose any chapter, or read them in order.')
st.session_state.setdefault('care_basics_chapter', 0)
st.session_state.setdefault('care_basics_picker', st.session_state.care_basics_chapter)


def choose_chapter():
    st.session_state.care_basics_chapter = st.session_state.care_basics_picker


def move_chapter(offset):
    index = max(0, min(len(CHAPTERS) - 1, st.session_state.care_basics_chapter + offset))
    st.session_state.care_basics_chapter = index
    st.session_state.care_basics_picker = index


st.selectbox('Choose a chapter', range(len(CHAPTERS)),
             format_func=lambda index: f'{index + 1} · {CHAPTERS[index]["title"]}',
             key='care_basics_picker', on_change=choose_chapter)
index = st.session_state.care_basics_chapter
chapter = CHAPTERS[index]
st.progress((index + 1) / len(CHAPTERS), text=f'Chapter {index + 1} of {len(CHAPTERS)}')
st.header(chapter['title'])
st.write(chapter['intro'])
st.image(illustration(chapter['diagram']), width='stretch')
st.caption('Simplified educational illustration; not a diagnostic image.')
st.info(chapter['takeaway'], icon=':material/lightbulb:')
for section in chapter['sections']:
    st.subheader(section['title'])
    st.markdown(section['body'])
    st.caption('Read more: ' + ' · '.join(f'[{SOURCES[key][0]}]({SOURCES[key][1]})' for key in section['sources']))

st.subheader('Questions to bring to your care team')
st.markdown('\n'.join(f'- {question}' for question in chapter['questions']))
previous, next_page = st.columns(2)
previous.button('Previous chapter', key='basics_previous', disabled=index == 0,
                on_click=move_chapter, args=(-1,), width='stretch')
next_page.button('Next chapter', key='basics_next', disabled=index == len(CHAPTERS) - 1,
                 on_click=move_chapter, args=(1,), width='stretch')
st.download_button('Download all six chapters', data=reading_guide(),
                   file_name='cancer-basics-reading-guide.md', mime='text/markdown')
st.caption(f'Sources checked {SOURCES_CHECKED}. This educational guide supports conversations with your care team. Individual treatment plans depend on your diagnosis and health.')
