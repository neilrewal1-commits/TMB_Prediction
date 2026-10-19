"""Plain-language educational chapters. Sources checked 2026-10-18."""
SOURCES_CHECKED = '2026-10-18'

NCI = 'https://www.cancer.gov'
SOURCES = {
    'what': ('NCI: What Is Cancer?', NCI + '/about-cancer/understanding/what-is-cancer'),
    'acs': ('American Cancer Society: What Is Cancer?', 'https://www.cancer.org/cancer/understanding-cancer/what-is-cancer.html'),
    'genetics': ('NCI: The Genetics of Cancer', NCI + '/about-cancer/causes-prevention/genetics'),
    'risk': ('NCI: Risk Factors for Cancer', NCI + '/about-cancer/causes-prevention/risk'),
    'tobacco': ('NCI: Tobacco', NCI + '/about-cancer/causes-prevention/risk/tobacco'),
    'alcohol': ('NCI: Alcohol', NCI + '/about-cancer/causes-prevention/risk/alcohol'),
    'infection': ('NCI: Infectious Agents', NCI + '/about-cancer/causes-prevention/risk/infectious-agents'),
    'sun': ('NCI: Sunlight', NCI + '/about-cancer/causes-prevention/risk/sunlight'),
    'prevention': ('NCI: Cancer Prevention Overview', NCI + '/about-cancer/causes-prevention/patient-prevention-overview-pdq'),
    'stage': ('NCI: Cancer Staging', NCI + '/about-cancer/diagnosis-staging/staging'),
    'spread': ('NCI: Metastatic Cancer', NCI + '/types/metastatic-cancer'),
    'grade': ('NCI: Tumor Grade', NCI + '/about-cancer/diagnosis-staging/diagnosis/tumor-grade'),
    'recurrence': ('NCI: Recurrent Cancer', NCI + '/types/recurrent-cancer'),
    'diagnosis': ('NCI: Tests and Procedures Used to Diagnose Cancer', NCI + '/about-cancer/diagnosis-staging/diagnosis'),
    'markers': ('NCI: Tumor Markers', NCI + '/about-cancer/diagnosis-staging/diagnosis/tumor-markers-fact-sheet'),
    'biomarkers': ('NCI: Biomarker Testing for Cancer Treatment', NCI + '/about-cancer/treatment/types/biomarker-testing-cancer-treatment'),
    'inherited': ('NCI: Genetic Testing for Inherited Cancer Risk', NCI + '/about-cancer/causes-prevention/genetics/genetic-testing-fact-sheet'),
    'screening': ('NCI: Cancer Screening', NCI + '/about-cancer/screening'),
    'treatments': ('NCI: Types of Cancer Treatment', NCI + '/about-cancer/treatment/types'),
    'surgery': ('NCI: Surgery for Cancer', NCI + '/about-cancer/treatment/types/surgery'),
    'radiation': ('NCI: Radiation Therapy', NCI + '/about-cancer/treatment/types/radiation-therapy'),
    'chemo': ('NCI: Chemotherapy', NCI + '/about-cancer/treatment/types/chemotherapy'),
    'targeted': ('NCI: Targeted Therapy', NCI + '/about-cancer/treatment/types/targeted-therapies'),
    'immune': ('NCI: Immunotherapy', NCI + '/about-cancer/treatment/types/immunotherapy'),
    'palliative': ('NCI: Palliative Care', NCI + '/about-cancer/advanced-cancer/care-choices/palliative-care-fact-sheet'),
    'trials': ('NCI: Clinical Trials', NCI + '/research/participate/clinical-trials'),
    'questions': ('NCI: Questions to Ask about Treatment', NCI + '/about-cancer/treatment/questions'),
    'feelings': ('NCI: Emotions and Cancer', NCI + '/about-cancer/coping/feelings'),
    'stomach': ('NCI: What Is Stomach Cancer?', NCI + '/types/stomach'),
    'stomach_risk': ('NCI: Stomach Cancer Causes and Risk Factors', NCI + '/types/stomach/causes-risk-factors'),
    'stomach_symptoms': ('NCI: Stomach Cancer Symptoms', NCI + '/types/stomach/symptoms'),
    'stomach_tests': ('NCI: Stomach Cancer Diagnosis', NCI + '/types/stomach/diagnosis'),
    'stomach_stage': ('NCI: Stomach Cancer Stages', NCI + '/types/stomach/stages'),
    'stomach_treatment': ('NCI: Treatment of Stomach Cancer', NCI + '/types/stomach/treatment'),
    'gastric_pdq': ('NCI: Gastric Cancer Treatment — Professional PDQ', NCI + '/types/stomach/hp/stomach-treatment-pdq'),
    'nutrition': ('NCI: Nutrition During Cancer', NCI + '/about-cancer/treatment/side-effects/nutrition'),
}


def section(title, body, *sources):
    return {'title': title, 'body': body.strip(), 'sources': list(sources)}


CHAPTERS = [
    {
        'title': 'What cancer is', 'diagram': 'cells',
        'intro': 'Start with cells, learn the words used in reports, and see why cancer is a family of diseases.',
        'takeaway': 'The cancer type describes what the disease is. The stage describes its extent. Neither a symptom nor the word “tumor” tells the whole story.',
        'sections': [
            section('Your body is built from cells', '''
Cells are tiny living units that make up organs and tissues. They usually respond to instructions about when to divide, repair damage, or stop growing. Cancer develops when some cells lose enough of these controls to keep multiplying in ways that harm the body.

The important issue is their behavior, not simply that a cell looks unusual. Cancer cells may invade neighboring tissue, disrupt an organ, or spread elsewhere. Many cancers form a lump called a tumor, but some blood cancers do not form one solid lump. A normal blood result cannot, by itself, rule out every type of cancer.
''', 'what', 'markers'),
            section('A lump is not automatically cancer', '''
A **benign** tumor is a growth that does not invade nearby tissue or spread to distant organs. A **malignant** tumor is cancerous. Benign growths can still cause problems because of their size or location, so “benign” does not always mean “needs no care.”

Other changes, including cysts and precancerous tissue changes, are different from an invasive cancer diagnosis. A scan or examination can find a change that needs investigation. The words “mass,” “lesion,” and “abnormality” describe a finding; they do not all mean confirmed cancer. Understanding the exact diagnosis helps avoid treating every unfamiliar word as the same problem.
''', 'what', 'acs'),
            section('There are many different cancers', '''
Cancers are commonly named for the place or kind of cell where they began. A carcinoma begins in cells lining an organ or body surface. A sarcoma arises in supporting tissues such as bone or muscle. Leukemia, lymphoma, and myeloma are groups of cancers affecting blood-forming or immune cells.

The name matters because different cancers behave differently and respond to different treatments. Two people with a growth in the same organ may have different subtypes. Even when the diagnosis sounds similar, the details of the cells and their markers may lead to different care discussions. “Cancer” is the starting category, not a complete treatment plan.
''', 'acs'),
            section('Genetic does not always mean inherited', '''
Genes are parts of DNA that help guide how cells work. Changes in genes that control growth, repair, and survival can contribute to cancer. Some changes develop during a person's lifetime; others can be inherited from a parent.

A change found in a tumor does not automatically mean it is present throughout the body or can be passed to children. Likewise, inheriting a risk-related change is not the same as inheriting cancer itself. Tumor testing and inherited-risk testing answer different questions. If a report mentions a gene change, ask which type of testing was performed before drawing conclusions about relatives.
''', 'genetics'),
            section('Understanding a diagnosis takes more than one conversation', '''
A new diagnosis can bring information faster than anyone can absorb it. Feeling worried, numb, angry, or unsure what to ask is common. You can request an explanation in everyday words, keep copies of reports, and bring someone you trust to a visit.

It can help to separate three questions: What has been confirmed? What is still being investigated? What happens next? Writing these down makes the discussion more manageable. Support from counselors, social workers, family, or support groups can be part of care from the beginning. Needing support does not mean that you are coping badly.
''', 'feelings'),
        ],
        'questions': ['What is the exact cancer type and subtype?', 'Which findings are confirmed, and which need another test?', 'Can I have a copy of the pathology and imaging reports?'],
    },
    {
        'title': 'Causes, risk and prevention', 'diagram': 'causes',
        'intro': 'Understand how risk factors influence chances, without turning them into blame or guarantees.',
        'takeaway': 'A risk factor changes the chance of disease. It does not prove why one person developed cancer, and reducing risk cannot remove every possibility.',
        'sections': [
            section('Risk describes chances, not certainty', '''
Cancer usually develops through a combination of changes over time. Age, inherited biology, exposures, infections, and other factors can all contribute. Some can be changed; others cannot. Having a risk factor does not guarantee cancer, and people without an obvious risk factor can still develop it.

Research sometimes finds an association between an exposure and cancer. An association alone does not prove that the exposure caused a particular person's illness. There is often no single explanation for an individual diagnosis. Risk information is most useful when it guides prevention, screening discussions, or family counseling rather than blame.
''', 'risk'),
            section('Tobacco and alcohol are important exposures', '''
Tobacco smoke contains substances that damage cells and increase the risk of several cancers, not only lung cancer. Exposure to other people's smoke also matters. Stopping tobacco use can improve health, and support can make quitting more achievable.

Alcohol is also linked to several cancers. Drinking less lowers exposure; avoiding alcohol is an option for reducing alcohol-related cancer risk. Neither smoking history nor alcohol use should be used to assume a diagnosis or to judge someone who has cancer. A care team can discuss practical changes and support without making treatment conditional on being a “perfect” patient.
''', 'tobacco', 'alcohol'),
            section('Some infections can increase cancer risk', '''
Certain long-lasting infections can damage tissue or affect cell behavior. Examples include some types of human papillomavirus (HPV), hepatitis B and C viruses, and Helicobacter pylori bacteria. The infection, the part of the body affected, and the person's other risks all matter.

This does not mean that most people with an infection will develop cancer. It also does not mean cancer itself is something you ordinarily catch from another person. Vaccines are available against HPV and hepatitis B, and some infections can be treated. Ask about the prevention or testing that fits your age, health history, and local guidance.
''', 'infection'),
            section('Sun exposure is another preventable risk', '''
Ultraviolet radiation from sunlight and tanning devices can damage skin cells. Protection includes shade, clothing, and appropriate sunscreen use; tanning beds are not a safe way to prepare for sun exposure. Skin protection matters across skin tones, although individual risks differ.

A changing skin finding should be assessed rather than diagnosed from an educational picture. This chapter explains risk reduction, not a rule for deciding whether a particular mole is cancer. A clinician can advise how personal history changes the need for skin checks.
''', 'sun'),
            section('Prevention is a set of habits and conversations', '''
Physical activity, a balanced eating pattern, and maintaining a healthy weight can support health and lower the risk of some cancers. Prevention also includes reducing harmful exposures and discussing recommended vaccines and screening. No food, supplement, or daily routine can guarantee that cancer will never occur.

Some people with a clearly defined high inherited risk may discuss additional preventive options with specialists. These decisions differ from general lifestyle advice and depend on the specific risk. Start with achievable changes and a plan that fits your life. If cancer is already diagnosed, prevention information should complement treatment rather than replace it.
''', 'prevention'),
            section('Family history can guide the next question', '''
Several relatives with related cancers, or cancer at unusually young ages, may be a reason to discuss genetic counseling. Families can also share exposures or have common cancers by chance. A family history does not prove that a hereditary syndrome is present.

Bring the cancer types and approximate ages at diagnosis if you know them. A genetics professional can help distinguish a tumor-only change from an inherited finding and explain what information may be useful for relatives.
''', 'genetics'),
        ],
        'questions': ['Which risk factors can I realistically change?', 'Does my family history suggest genetic counseling?', 'Which screening tests or vaccines are appropriate for me?'],
    },
    {
        'title': 'Growth, spread and progression', 'diagram': 'spread',
        'intro': 'Learn how cancer extent is described and why stage, grade, and changes over time mean different things.',
        'takeaway': 'Stage is a description, not a countdown. Cancers do not all grow at the same speed or follow an inevitable sequence through every stage.',
        'sections': [
            section('Local growth and distant spread are different', '''
A cancer can grow within the organ where it began and invade nearby structures. Some cancer cells can also enter blood or lymph channels and reach another part of the body. When they establish cancer in a distant site, this is called metastasis.

Not every cancer cell that travels forms a new tumor, and not every cancer spreads. The possible routes and common sites differ between cancer types. A small diagram can show how spread is possible, but it cannot predict an individual person's course or how quickly a disease might change.
''', 'spread'),
            section('A cancer keeps the identity of its starting site', '''
Cancer that starts in the breast and later appears in the lung is generally called metastatic breast cancer, not a new lung cancer. This distinction matters because treatment often follows the biology of the original cancer.

A finding in another organ is not automatically a metastasis. The care team may need imaging comparisons, tissue testing, or other evidence to determine what it represents. The location of a finding and the diagnosis of that finding are separate pieces of information. Ask how the team established the link to the original disease.
''', 'spread'),
            section('What a stage describes', '''
For many solid cancers, staging describes the primary tumor, nearby lymph nodes, and whether cancer has spread to distant sites. The letters **T**, **N**, and **M** often represent those three parts. Stage groups may use numbers such as I through IV, but the exact definitions depend on the cancer and staging system.

Some blood cancers and brain tumors use other systems. A clinical stage uses information available before certain treatments; a pathological stage may add findings from an operation. The stage recorded at diagnosis is kept in the medical history, while later changes are described separately. A stage number alone does not explain every treatment choice or predict one person's outcome.
''', 'stage'),
            section('Grade describes how the cells look', '''
Grade is based on features seen when tissue is examined, often including how different the cancer cells look from normal cells. In many cancers, higher-grade cells are more abnormal and may behave more aggressively. The grading rules and their usefulness depend on the specific cancer.

Grade is not interchangeable with stage. A tumor may be localized but have a high grade, or have spread despite a lower grade. A pathology report may describe differentiation, which concerns how closely cells resemble their normal counterparts. Your team uses this information with the rest of the assessment, not as a replacement for staging.
''', 'grade'),
            section('Response, progression and recurrence describe change', '''
During follow-up, clinicians compare symptoms, examinations, scans, or laboratory results over time. Cancer that returns after a period without detectable disease is called recurrent cancer. Recurrence may be near the original site, in nearby tissues or nodes, or farther away.

The next evaluation depends on the type of cancer and where it has returned. A suspected recurrence often leads to further testing before a plan is chosen. Keep the dates of your reports together: an older finding and a newer finding should not be treated as if they came from the same examination. Ask your team what comparison was made and what the change means for the next decision.
''', 'recurrence'),
        ],
        'questions': ['Which staging system and edition were used?', 'Is this clinical or pathological staging?', 'What changed compared with the previous examination?'],
    },
    {
        'title': 'Tests, diagnosis and biomarkers', 'diagram': 'tests',
        'intro': 'See how different tests contribute different pieces of evidence, from a first finding to a treatment discussion.',
        'takeaway': 'A scan, a tissue sample, and a blood test answer different questions. Good interpretation combines the right tests with the history and examination.',
        'sections': [
            section('There is no single test for every cancer', '''
An evaluation may begin with symptoms, a physical examination, or a screening result. Clinicians choose tests based on the concern and the person's history. Imaging such as ultrasound, CT, MRI, or PET can show the location and features of a finding, but different scans provide different information.

An image can suggest where to investigate; it does not always establish exactly what the cells are. A radiology report records the specialist's interpretation of the examination. Reading that written report alongside other test results is different from looking at one selected scan picture.
''', 'diagnosis'),
            section('Why a biopsy is often important', '''
A biopsy removes cells or tissue for examination. A pathologist studies the sample to help identify whether cancer is present and, if so, its type and other features. Samples may be taken with a needle, through an endoscope, or during an operation.

The method depends on the suspected disease and the safest useful way to obtain tissue. A sample represents the material collected, so the team considers whether it answers the question being asked. Ask what the pathology report confirmed, whether more information is pending, and whether additional testing can use the same sample.
''', 'diagnosis'),
            section('Blood tests and tumor markers have specific jobs', '''
Blood tests may assess blood cells, organ function, or certain substances associated with disease. A tumor marker may help with diagnosis, treatment planning, or monitoring in a particular setting. Some markers also rise in noncancerous conditions, and some cancers do not produce a useful marker.

For that reason, a marker is interpreted with other evidence. A normal result is not a universal cancer-free certificate, and one raised value is not a diagnosis by itself. Trends can be helpful, but the meaning of a trend depends on the marker and the situation in which it was measured.
''', 'markers'),
            section('Biomarkers can help identify treatment possibilities', '''
Biomarker testing looks for features such as certain gene changes or proteins in a cancer. Some findings may identify a treatment option or a clinical trial. Others may not have a treatment linked to them. Different areas of a tumor, or samples taken at different times, can have different features.

A result that matches a treatment target is one part of a decision, not a guarantee of benefit. The cancer type, stage, previous treatment, health, and drug-specific requirements still matter. Ask which results are actionable, which are uncertain, and whether more testing would change the plan.
''', 'biomarkers'),
            section('Inherited-risk testing is a separate conversation', '''
Testing for inherited cancer risk usually examines a blood or saliva sample for changes that may be present throughout the body. It is different from testing a tumor to help select treatment, although one result can sometimes lead to a discussion about the other.

Genetic counseling can explain possible results, privacy concerns, and implications for relatives. Not everyone needs inherited-risk testing. The reason for a test and how each possible result would be used are worth discussing before it is ordered.
''', 'inherited'),
            section('Screening and diagnostic testing are not the same', '''
Screening looks for signs of some cancers or precancerous changes before symptoms appear. A diagnostic test investigates an existing concern. Which screening is useful depends on the cancer, age, risk, and applicable recommendations.

A positive screening test often needs follow-up; it does not automatically mean cancer is present. Screening also has possible harms, including false alarms and detection of disease that might never cause problems. If you already have symptoms, ask how they should be evaluated rather than waiting for the next routine screening appointment.
''', 'screening'),
        ],
        'questions': ['What question will this test answer?', 'What does the pathology report establish?', 'Would a biomarker or inherited-risk result change my care?'],
    },
    {
        'title': 'Treatment approaches and daily life', 'diagram': 'care',
        'intro': 'Compare the main approaches and understand how cancer treatment, symptom relief, and everyday support can work together.',
        'takeaway': 'A care plan has a purpose: for example, removing cancer, lowering recurrence risk, controlling disease, or relieving symptoms. Ask which purpose applies to each part of the plan.',
        'sections': [
            section('Start with the goal of care', '''
Treatment is chosen for a specific cancer and person, not simply for the word “cancer.” The type, extent of disease, previous treatment, health, test results, and preferences help shape the discussion. Some people receive one main treatment; others receive several in sequence or together.

It helps to know what each component is meant to achieve and how the team will assess whether it is working. Understanding the goal also makes it easier to compare benefits, burdens, timing, and alternatives. The same treatment name can have a different purpose in another person's situation.
''', 'treatments'),
            section('Local approaches: surgery and radiation', '''
**Surgery** removes cancer or tissue from a particular area. It can also help establish the extent of disease or relieve a problem caused by a tumor. Its role depends on whether the cancer can be removed safely and usefully.

**Radiation therapy** uses radiation to damage cancer cells. It may treat a particular area, reduce the chance of a local return, or help relieve symptoms. External-beam treatment and treatments using radioactive material are different techniques. Local approaches can be combined with medicines when the care plan needs to address more than one site or goal.
''', 'surgery', 'radiation'),
            section('Chemotherapy acts on cancer cells in different settings', '''
Chemotherapy uses medicines that kill or slow cancer cells, often by affecting cell division. It can be used before another treatment, afterward, or as a main treatment. Different drugs and schedules have different purposes and side effects.

Because some healthy cells are affected too, monitoring and supportive medicines are part of the plan. Side effects do not reliably show how well chemotherapy is working. Ask how effectiveness will be assessed, which symptoms to report, and whom to contact between visits. Do not change a prescribed schedule based only on an educational overview.
''', 'chemo'),
            section('Targeted therapy and immunotherapy work differently', '''
**Targeted therapy** acts on a feature that helps cancer grow or survive. A relevant marker may need to be confirmed before a particular medicine is considered. Cancer can also change over time, so the team may reassess which targets remain useful.

**Immunotherapy** helps parts of the immune system act against cancer. It is useful in some settings, not every cancer. Immune effects can also affect healthy organs. “Targeted” and “immune” do not mean side-effect free. These treatments have their own eligibility checks and monitoring, and a gene report by itself cannot select the right drug.
''', 'targeted', 'immune'),
            section('Other approaches fit particular cancers', '''
Hormone therapy is used for some cancers that rely on hormone signals. Blood stem-cell transplants can restore blood-forming cells after certain treatments. Some cellular therapies modify or use immune cells to attack particular cancers.

These approaches are not interchangeable, and not everyone is a candidate for them. The important question is why an approach matches the exact disease and treatment setting. More treatment names do not necessarily mean more appropriate options for an individual person.
''', 'treatments'),
            section('Clinical trials are another way to discuss options', '''
Clinical trials are research studies that evaluate questions about care. Some test new treatments, combinations, or ways of using established treatments. Eligibility rules define who may take part, and participation involves a consent discussion.

Trials are not limited to people who have exhausted all standard options. Ask what the study is comparing, what is known, what remains unknown, and how visits, costs, or travel could affect daily life. Learning about a trial does not commit you to joining it, and choosing whether to participate is a separate decision from receiving routine care.
''', 'trials'),
            section('Symptom relief and support belong in the plan', '''
Palliative care addresses symptoms, stress, and quality of life. It can be provided alongside treatment directed at the cancer and is not the same thing as stopping cancer treatment. Pain, nausea, fatigue, sleep, and emotional concerns are all reasonable topics to raise.

Practical support may involve nutrition professionals, counselors, rehabilitation specialists, social workers, or help with transport and costs. A person does not need to wait until a crisis to ask for support. Discuss how treatment may affect work, caring responsibilities, fertility, eating, or activities that matter to you.
''', 'palliative', 'feelings'),
            section('Make the decision understandable', '''
Ask the team to compare the expected benefits, important risks, alternatives, and likely effects on daily life. A second opinion may help clarify a complicated choice. Bring your priorities to the conversation, including what you hope treatment will make possible.

Before leaving, check that you know the next step, its timing, and whom to contact with questions. Request written instructions and a contact plan for treatment-related symptoms. Shared decision-making means that medical evidence and the person's goals both have a place in the discussion.
''', 'questions'),
        ],
        'questions': ['What is the goal of each treatment?', 'What alternatives or clinical trials should we discuss?', 'Who can help with symptoms, nutrition, costs and daily life?'],
    },
    {
        'title': 'Stomach cancer in focus', 'diagram': 'stomach',
        'intro': 'A closer look at gastric cancer: the stomach lining, H. pylori, endoscopy, staging, treatment markers, and eating well.',
        'takeaway': 'For stomach cancer, the tissue diagnosis, depth of growth, lymph nodes, distant spread, and treatment markers each contribute different information. A TMB category cannot replace those details.',
        'sections': [
            section('What gastric cancer means', '''
The stomach stores and mixes food after it passes through the esophagus. “Gastric” means related to the stomach. Most stomach cancers are adenocarcinomas, which begin in gland-forming cells in the inner lining. The exact location and cell pattern can matter for care.

Not every cancer found in the stomach is an adenocarcinoma. Lymphoma, gastrointestinal stromal tumors (GIST), and neuroendocrine tumors are different diseases with different treatment approaches. Cancers near the junction between the esophagus and stomach may also need a different staging discussion. Ask for the precise pathology name rather than relying only on “stomach tumor.”
''', 'stomach'),
            section('Important causes and risk factors', '''
Long-standing Helicobacter pylori (H. pylori) infection is an important risk factor for some stomach cancers. In some people, inflammation is followed by changes in the stomach lining. Most people with H. pylori do not develop stomach cancer. Treating the infection can reduce the risk of certain gastric cancers, but it does not replace evaluation of concerning symptoms.

Other risks include smoking, certain chronic stomach conditions, family history, and some inherited syndromes. Risks differ between the upper stomach and other parts of the organ. Ask whether H. pylori testing, treatment, or genetic counseling is relevant to your own history.
''', 'stomach_risk'),
            section('Symptoms are a reason to investigate, not a diagnosis', '''
Early stomach cancer may have few symptoms. Possible symptoms include persistent indigestion or discomfort, feeling full quickly, reduced appetite, nausea, unexplained weight loss, or difficulty swallowing. These problems can also have causes other than cancer.

Persistent or worsening symptoms deserve a clinical assessment. Bleeding, such as vomiting blood or black stools, needs prompt medical attention. The useful next question is what evaluation is needed, not whether a symptom list can confirm the disease. Tell the clinician how long symptoms have lasted and whether eating, weight, or everyday activity has changed.
''', 'stomach_symptoms'),
            section('How stomach cancer is diagnosed', '''
Upper endoscopy allows a clinician to inspect the stomach using a flexible tube with a camera. Tissue samples can be collected for a biopsy. The pathology examination helps determine whether cancer is present and identifies its type.

Other investigations may assess disease extent or help plan care. These can include imaging, endoscopic ultrasound, or selected procedures depending on the situation. Biomarker tests may use the tissue sample too. Keep the endoscopy, pathology, imaging, and laboratory reports together: each provides a different part of the assessment. Ask whether the samples are sufficient for the tests needed before treatment decisions.
''', 'stomach_tests'),
            section('Depth, lymph nodes and spread shape the stage', '''
The stomach wall has layers. For gastric adenocarcinoma, staging considers how deeply the cancer extends, whether nearby lymph nodes contain cancer, and whether disease is present at distant sites. The tumor's width alone cannot supply all of this information.

Clinical staging, staging after an operation, and assessment after treatment are not identical. The number of positive nodes also needs to be understood alongside how many were examined. An enlarged node on a scan is not the same as a pathology-confirmed positive node. Ask which staging system applies, what evidence supports it, and whether findings refer to the same treatment episode.
''', 'stomach_stage'),
            section('Treatment approaches and markers', '''
Some carefully selected early stomach cancers can be treated through an endoscope. Surgery may remove part or all of the stomach and nearby lymph nodes. Chemotherapy, radiation, targeted therapy, or immunotherapy may be considered in different settings; treatment before and after surgery serves a different purpose from treatment for advanced disease.

For advanced gastric adenocarcinoma, testing may include HER2, PD-L1, mismatch-repair or microsatellite-instability status, and CLDN18.2. These results can affect which options are discussed. A positive marker does not automatically select a medicine: treatment setting, prior therapy, health, and drug-specific checks still matter. The app's high/low TMB research result is not a clinical mutations-per-megabase measurement and cannot choose treatment on its own.
''', 'stomach_treatment', 'gastric_pdq'),
            section('Eating, weight and recovery need attention', '''
Stomach cancer and its treatment can affect appetite, digestion, weight, and the ability to obtain enough nutrients. After stomach surgery, meal size, eating patterns, and nutrient absorption may change. Nutrition care is part of recovery, not an optional extra.

A dietitian can help adapt food choices and meal patterns to symptoms and treatment. The team may also assess nutrient deficiencies and decide whether supplements or other support are needed. Avoid starting restrictive diets or high-dose supplements without discussing them. Bring a record of weight changes and problems such as nausea, swallowing difficulty, or feeling full early to appointments.
''', 'nutrition'),
        ],
        'questions': ['What exact stomach cancer type and location were found?', 'Which staging findings and biomarkers are confirmed?', 'Should I see a dietitian or discuss H. pylori and family history?'],
    },
]


def reading_guide():
    lines = ['# Cancer Basics', 'Sources checked: ' + SOURCES_CHECKED,
             'Educational information for discussion with your care team.', '']
    for index, chapter in enumerate(CHAPTERS, 1):
        lines += [f"## {index}. {chapter['title']}", chapter['intro'], '', chapter['takeaway'], '']
        for block in chapter['sections']:
            lines += ['### ' + block['title'], block['body'], '']
            lines += [f'[{SOURCES[key][0]}]({SOURCES[key][1]})' for key in block['sources']]
        lines += ['### Questions for your care team', *['- ' + q for q in chapter['questions']], '']
    return '\n\n'.join(lines)
