import os
from sourcing.ScriptScraper import ScriptScraper
from sourcing.SumScraper import SumScraper
from google import genai
from google.genai import types
import json


# Parses response to only have JSON. Could be fixed using schema, will be done in next version.
class GeminiAnalysis:
    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    def RunAnalysis(self, movie_title, wikipedia_summary, movie_script):
        scripts = ScriptScraper()
        summary = SumScraper()
        example_scripts = {
            "Joker": "sourcing/ExampleScripts/joker_2019.pdf",
            "Whiplash": "sourcing/ExampleScripts/whiplash_2014.pdf",
            "Midsommar": "sourcing/ExampleScripts/midsommar_2019.pdf"
        }
        scripts_text = {movie: scripts.pdf_to_text(path) for movie, path in example_scripts.items()}
        few_shot_prompt = f"""
            You are an AI trained to detect emotional triggers in movies to assist users with PTSD and trauma sensitivity. 
            You have access to general movie knowledge, including themes, events, and content warnings from your pre-trained knowledge. 
            Use both your **internal knowledge of films** and the provided **Wikipedia summary & script** to accurately determine whether specific triggers appear in the film. 
            Follow these steps: 
            **Analyze the Wikipedia summary & script** to detect explicit mentions of triggers.
            **Compare this with your general knowledge** of the movie.
            **Only mark a trigger as (1) if it is explicitly mentioned in the Wikipedia summary, the script, or if it is extremely well-known from widely accepted sources. If unsure, mark it as (0). Do not guess.**
            **Return the final trigger list in JSON format**.

            Each trigger is labeled as:
            - `1` if present in the movie
            - `0` if not present

            Below are three examples to help guide your analysis.

            ---

            ### **Example 1**
            Movie: Joker (2019)
            Wikipedia Summary:
            {summary.get_wikipedia_summary("Joker", "Todd Phillips", "tt7286456")}

            Script:
            {scripts_text['Joker']}

            ### Output
            Triggers:
            {{
               "a cat dies": 0, "a dog dies": 0, "a horse dies": 0, "a plane crashes":  0, “an animal dies”: 0, “animals are abused”: 0, “someone breaks a bone”: 1, “someone falls to their death”: 0, “someone vomits”: 0, “teeth are damaged”: 0, “there are bugs”: 0, “there are incestuous relationships”: 0, “there's addiction”: 1, “there's dog fighting”: 0, “a baby cries”: 0, “a baby is stillborn”: 0, “a car crashes”: 1, “A child's dear toy is destroyed”: 0, “a kid dies”: 0, “a mentally ill person is violent”: 1, “a minority is misrepresented”: 0, “a parent dies”: 1, “a person is hit by a car”: 1, “a pet dies”: 0, “a pregnant person dies”: 0, “alcohol abuse”: 0, “autism specific abuse”: 0, “heads get squashed”: 1, “needles/syringes are used”: 0, “someone asphyxiates”: 1, “someone attempts suicide”: 0, “someone becomes unconscious”: 0, “someone dies by suicide”: 0, “someone drowns”: 0, “someone gets gaslighted”: 1, “someone has a seizure”: 1, “someone has a stroke”: 1, “someone has an abortion”: 0, “someone has an anxiety attack”: 1, “someone has an eating disorder”: 1, “someone has cancer”: 0, “someone has dementia/Alzheimer's”: 0, “someone is buried alive”: 0, “someone is burned alive”: 0, “someone is crushed to death”: 0, “someone is drugged”: 0, “someone is homeless”: 1, “someone is kidnapped”: 0, “someone is misgendered”: 0, “someone is raped onscreen”: 0, “someone is restrained”: 1, “someone is sexually assaulted”: 0, “someone is stalked”: 1, “someone miscarries”: 0, “someone overdoses”: 0, “someone says "I'll kill myself"”: 1, “someone says the n-word”: 0, “someone self harms”: 1, “someone speaks hate speech”: 0, “someone struggles to breathe”: 1, “someone suffers from PTSD”: 0, “someone uses drugs”: 1, “the abused becomes the abuser”: 1, “the black guy dies first”: 0, “the r-slur is used”: 0, “there are "Man in a dress" jokes”: 0, “there are hangings”: 0, “there are homophobic slurs”: 0, “there are transphobic slurs”: 0, “there is copaganda”: 0, “there's a claustrophobic scene”: 1, “there's a dead animal”: 0, “there's a hospital scene”: 1, “there's a mental institution scene”: 1, “there's an explosion”: 0, “there's ableist language or behavior”: 1, “there's amputation”: 0, “there's anti-abortion themes”: 0, “there's antisemitism”: 0, “there's bestiality”: 0, “there's blood/gore”: 1, “there's body dysmorphia”: 1, “there's body horror”: 0, “there's cannibalism”: 0, “there's child abuse”: 1, “there's childbirth”: 0, “there's domestic violence”: 1, “there's eye mutilation”: 1, “there's fat jokes”: 0, “there's fat suits”: 0, “there's finger/toe mutilation”: 0, “there's genital trauma/mutilation”: 0, “there's gun violence”: 1, “there's shaving/cutting”: 0, “there's torture”: 1, “a child is abandoned by a parent or guardian”: 1, “a family member dies”: 1, “a minor is sexualized”: 0, “a trans person is depicted predatorily”: 0, “dissociative identity disorder misrepresentation”: 0, “rape is mentioned”: 0, “sexual assault on men is a joke”: 0, “someone dies”: 1, “someone falls down stairs”: 0, “someone has a chronic illness”: 1, “someone has a mental illness”: 1, “someone is held under water”: 0, “someone is terminally ill”: 0, “the abused forgives their abuser”: 0, “there are 9/11 depictions”: 0, “there's aphobia”: 0, “someone cheats on their significant other”: 0, “there's blackface”: 0, “there's gender dysphoria”: 0, “there's deadnaming”: 0, “there's pedophilia”: 0, “someone is slapped”: 0, “someone is brutalized for spectacle”: 0, “an animal is abandoned”: 0, “an LGBT person is outed”: 0, “autism is misrepresented”: 0, “hands are damaged”: 0, “somebody is choked”: 1, “someone dislocates something”: 0, “someone has a meltdown”: 1, “someone is stabbed”: 1, “someone's throat is mutilated”: 1, “someone goes to therapy”: 0, “there's abusive parents”: 1, “there's BDSM”: 0, “there's decapitation”: 0, “there's incarceration”: 1   
            }}

            ---

            ### **Example 2**
            Movie: Whiplash (2014)
            Wikipedia Summary:
            {summary.get_wikipedia_summary("Whiplash", "Damien Chazelle", "tt258280")}

            Script:
            {scripts_text['Whiplash']}

            ### Output
            Triggers:
            {{
                "a cat dies": 0, "a dog dies": 0, "a horse dies": 0, "a plane crashes":  0, “an animal dies”: 0, “animals are abused”: 0, “someone breaks a bone”: 0, “someone falls to their death”: 0, “someone vomits”: 0, “teeth are damaged”: 0, “there are bugs”: 0, “there are incestuous relationships”: 0, “there's addiction”: 0, “there's dog fighting”: 0, “a baby cries”: 0, “a baby is stillborn”: 0, “a car crashes”: 1, “A child's dear toy is destroyed”: 0, “a kid dies”: 0, “a mentally ill person is violent”: 1, “a minority is misrepresented”: 0, “a parent dies”: 0, “a person is hit by a car”: 1, “a pet dies”: 0, “a pregnant person dies”: 0, “alcohol abuse”: 1, “autism specific abuse”: 1, “heads get squashed”: 0, “needles/syringes are used”: 0, “someone asphyxiates”: 0, “someone attempts suicide”: 0, “someone becomes unconscious”: 0, “someone dies by suicide”: 1, “someone drowns”: 0, “someone gets gaslighted”: 1, “someone has a seizure”: 0, “someone has a stroke”: 0, “someone has an abortion”: 0, “someone has an anxiety attack”: 1, “someone has an eating disorder”: 0, “someone has cancer”: 0, “someone has dementia/Alzheimer's”: 0, “someone is buried alive”: 0, “someone is burned alive”: 0, “someone is crushed to death”: 0, “someone is drugged”: 0, “someone is homeless”: 0, “someone is kidnapped”: 0, “someone is misgendered”: 0, “someone is raped onscreen”: 0, “someone is restrained”: 0, “someone is sexually assaulted”: 0, “someone is stalked”: 0, “someone miscarries”: 0, “someone overdoses”: 0, “someone says "I'll kill myself"”: 0, “someone says the n-word”: 0, “someone self harms”: 1, “someone speaks hate speech”: 1, “someone struggles to breathe”: 1, “someone suffers from PTSD”: 1, “someone uses drugs”: 0, “the abused becomes the abuser”: 0, “the black guy dies first”: 0, “the r-slur is used”: 1, “there are "Man in a dress" jokes”: 1, “there are hangings”: 0, “there are homophobic slurs”: 1, “there are transphobic slurs”: 0, “there is copaganda”: 0, “there's a claustrophobic scene”: 0, “there's a dead animal”: 0, “there's a hospital scene”: 0, “there's a mental institution scene”: 0, “there's an explosion”: 0, “there's ableist language or behavior”: 1, “there's amputation”: 0, “there's anti-abortion themes”: 0, “there's antisemitism”: 1, “there's bestiality”: 0, “there's blood/gore”: 1, “there's body dysmorphia”: 0, “there's body horror”: 0, “there's cannibalism”: 0, “there's child abuse”: 0, “there's childbirth”: 0, “there's domestic violence”: 1, “there's eye mutilation”: 0, “there's fat jokes”: 1, “there's fat suits”: 0, “there's finger/toe mutilation”: 1, “there's genital trauma/mutilation”: 0, “there's gun violence”: 0, “there's shaving/cutting”: 0, “there's torture”: 0, “a child is abandoned by a parent or guardian”: 1, “a family member dies”: 0, “a minor is sexualized”: 0, “a trans person is depicted predatorily”: 0, “dissociative identity disorder misrepresentation”: 0, “rape is mentioned”: 0, “sexual assault on men is a joke”: 1, “someone dies”: 0, “someone falls down stairs”: 1, “someone has a chronic illness”: 0, “someone has a mental illness”: 1, “someone is held under water”: 0, “someone is terminally ill”: 0, “the abused forgives their abuser”: 1, “there are 9/11 depictions”: 0, “there's aphobia”: 0, “someone cheats on their significant other”: 0, “there's blackface”: 0, “there's gender dysphoria”: 0, “there's deadnaming”: 0, “there's pedophilia”: 0, “someone is slapped”: 0, “someone is brutalized for spectacle”: 0, “an animal is abandoned”: 0, “an LGBT person is outed”: 0, “autism is misrepresented”: 0, “hands are damaged”: 1, “somebody is choked”: 0, “someone dislocates something”: 0, “someone has a meltdown”: 1, “someone is stabbed”: 0, “someone's throat is mutilated”: 0, “someone goes to therapy”: 0, “there's abusive parents”: 0, “there's BDSM”: 0, “there's decapitation”: 0, “there's incarceration”: 0
            }}

            ---

            ### **Example 3**
            Movie: Midsommar (2019)
            Wikipedia Summary:
            {summary.get_wikipedia_summary("Midsommar", "Ari Aster", "tt8772262")}

            Script:
            {scripts_text['Midsommar']}

            ### Output
            Triggers:
            {{
               "a cat dies": 0, "a dog dies": 0, "a horse dies": 0, "a plane crashes":  0, “an animal dies”: 1, “animals are abused”: 1, “someone breaks a bone”: 1, “someone falls to their death”: 1, “someone vomits”: 1, “teeth are damaged”: 1, “there are bugs”: 0, “there are incestuous relationships”: 1, “there's addiction”: 0, “there's dog fighting”: 0, “a baby cries”: 1, “a baby is stillborn”: 0, “a car crashes”: 0, “A child's dear toy is destroyed”: 0, “a kid dies”: 0, “a mentally ill person is violent”: 1, “a minority is misrepresented”: 0, “a parent dies”: 1, “a person is hit by a car”: 0, “a pet dies”: 0, “a pregnant person dies”: 0, “alcohol abuse”: 0, “autism specific abuse”: 0, “heads get squashed”: 1, “needles/syringes are used”: 0, “someone asphyxiates”: 1, “someone attempts suicide”: 1, “someone becomes unconscious”: 1, “someone dies by suicide”: 1, “someone drowns”: 0, “someone gets gaslighted”: 1, “someone has a seizure”: 0, “someone has a stroke”: 0, “someone has an abortion”: 0, “someone has an anxiety attack”: 1, “someone has an eating disorder”: 0, “someone has cancer”: 0, “someone has dementia/Alzheimer's”: 0, “someone is buried alive”: 0, “someone is burned alive”: 1, “someone is crushed to death”: 1, “someone is drugged”: 1, “someone is homeless”: 0, “someone is kidnapped”: 1, “someone is misgendered”: 0, “someone is raped onscreen”: 1, “someone is restrained”: 1, “someone is sexually assaulted”: 1, “someone is stalked”: 1, “someone miscarries”: 0, “someone overdoses”: 0, “someone says "I'll kill myself"”: 0, “someone says the n-word”: 0, “someone self harms”: 1, “someone speaks hate speech”: 0, “someone struggles to breathe”: 1, “someone suffers from PTSD”: 1, “someone uses drugs”: 1, “the abused becomes the abuser”: 1, “the black guy dies first”: 0, “the r-slur is used”: 0, “there are "Man in a dress" jokes”: 0, “there are hangings”: 1, “there are homophobic slurs”: 0, “there are transphobic slurs”: 0, “there is copaganda”: 0, “there's a claustrophobic scene”: 1, “there's a dead animal”: 1, “there's a hospital scene”: 0, “there's a mental institution scene”: 0, “there's an explosion”: 0, “there's ableist language or behavior”: 1, “there's amputation”: 1, “there's anti-abortion themes”: 0, “there's antisemitism”: 0, “there's bestiality”: 0, “there's blood/gore”: 1, “there's body dysmorphia”: 0, “there's body horror”: 1, “there's cannibalism”: 0, “there's child abuse”: 0, “there's childbirth”: 0, “there's domestic violence”: 1, “there's eye mutilation”: 1, “there's fat jokes”: 0, “there's fat suits”: 0, “there's finger/toe mutilation”: 1, “there's genital trauma/mutilation”: 0, “there's gun violence”: 0, “there's shaving/cutting”: 1, “there's torture”: 1, “a child is abandoned by a parent or guardian”: 0, “a family member dies”: 1, “a minor is sexualized”: 1, “a trans person is depicted predatorily”: 0, “dissociative identity disorder misrepresentation”: 0, “rape is mentioned”: 1, “sexual assault on men is a joke”: 0, “someone dies”: 1, “someone falls down stairs”: 0, “someone has a chronic illness”: 1, “someone has a mental illness”: 1, “someone is held under water”: 0, “someone is terminally ill”: 0, “the abused forgives their abuser”: 0, “there are 9/11 depictions”: 0, “there's aphobia”: 0, “someone cheats on their significant other”: 1, “there's blackface”: 0, “there's gender dysphoria”: 0, “there's deadnaming”: 0, “there's pedophilia”: 0, “someone is slapped”: 0, “someone is brutalized for spectacle”: 1, “an animal is abandoned”: 0, “an LGBT person is outed”: 0, “autism is misrepresented”: 0, “hands are damaged”: 1, “somebody is choked”: 0, “someone dislocates something”: 0, “someone has a meltdown”: 1, “someone is stabbed”: 0, “someone's throat is mutilated”: 0, “someone goes to therapy”: 0, “there's abusive parents”: 0, “there's BDSM”: 0, “there's decapitation”: 0, “there's incarceration”: 0   
            }}
            ---
        """
        user_prompt = f"""
            **ONLY use the following script and wikipedia summary in determining the triggers of {movie_title}.** Previous scripts and summaries are merely there for examples.
            **Now Analyze This Movie** 
            Movie: {movie_title}
            Wikipedia Summary:
            {wikipedia_summary}

            Script:
            {movie_script}

            Triggers:

            **Return only a valid JSON object. Do not guess. Only mark a trigger as present if it is clear in the script or summary.
            Once you havegenerated your json, check your answers and cross reference with this script: {movie_script} and this summary: {wikipedia_summary}. For any triggers that do not explicitly show up in these two sources, but that you have marked as '1',
            correct them to '0'. Return only the final generated JSON trigger list.
            """
        response = self.client.models.generate_content(
                model="gemini-2.5-pro-preview-03-25",
                config=types.GenerateContentConfig(
                    system_instruction=few_shot_prompt,
                    response_mime_type='application/json'),
                contents=user_prompt
        )
        json_start = response.text.find('{')
        json_end = response.text.find('}')

        json_cleaned = response.text[json_start:json_end+1]

        try:
            trigger_dict = json.loads(json_cleaned)
            return trigger_dict
        except json.JSONDecodeError as e:
            print("Failed to decode JSON:", e)
            print("Cleaned text:", json_cleaned)
            return None