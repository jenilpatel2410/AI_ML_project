from TTS.api import TTS
import torch
from TTS.tts.configs.xtts_config import XttsConfig, XttsAudioConfig, XttsArgs
from TTS.config.shared_configs import BaseDatasetConfig
from transformers import GPT2Model
from transformers.generation.utils import GenerationMixin

if not issubclass(GPT2Model, GenerationMixin):
    GPT2Model.__bases__ += (GenerationMixin,)

torch.serialization.add_safe_globals([
    XttsConfig,
    XttsAudioConfig,
    BaseDatasetConfig,
    XttsArgs,
])

device="cuda:0" if torch.cuda.is_available() else "cpu"

# Load pretrained voice cloning model
# tts = TTS(model_name="tts_models/multilingual/multi-dataset/your_tts", progress_bar=False)
tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2", progress_bar=False).to(device)

# checkpoint = torch.load('path_to_model.pth', map_location='cpu', weights_only=False)

# Reference audio sample (user's voice recording)
speaker_wav = "D:/AI_ML_project-main/Narendra_Modi_voice.ogg"  # 1–5 seconds of clear voice

# Text to synthesize in the cloned voice
# text = "*When Mr. Bilbo Baggins of Bag End announced that he would shortly be celebrating his eleventy-first birthday with a party of special magnificence, there was much talk and excitement in Hobbiton. Bilbo was very rich and very peculiar, and had been the wonder of the Shire for sixty years, ever since his remarkable disappearance and unexpected return. The riches he had brought back from his travels had now become a local legend, and it was popularly believed, whatever the old folk might say, that the Hill at Bag End was full of tunnels stuffed with treasure. And if that was not enough for fame, there was also his prolonged vigour to marvel at. Time wore on, but it seemed to have little effect on Mr. Baggins."

# text = "Sabse pehle, main aapko Gujarat ke Navsari mein swaagat karta hoon. Yeh sheher Gujarat ke ek mahatvapurna hisson mein se ek maana jaata hai. Yahan ke log mehnati hain aur gaon ke jeevan se pyaar karte hain. Navsari ki hawa mein ek shanti aur sauhardr ka bhaav hai. Yahan ke mele, utsav aur paramparaayein logon ko ek doosre se jod kar rakhti hain. Log yahan bahut samvedansheel aur madadgar hote hain. Jab hum Navsari aate hain, to yeh jagah ek ghar jaisi mehsoos hoti hai."
text = "सबसे पहले, मैं आपको गुजरात के नवसारी में स्वागत करता हूँ। यह शहर गुजरात के एक महत्वपूर्ण हिस्से के रूप में जाना जाता है। यहाँ के लोग मेहनती हैं और गाँव के जीवन से प्रेम करते हैं। नवसारी की हवा में एक शांति और सौहार्द्र की भावना है। यहाँ के मेले, उत्सव और परंपराएँ लोगों को एक-दूसरे से जोड़कर रखती हैं। लोग यहाँ बहुत संवेदनशील और मददगार होते हैं। जब हम नवसारी आते हैं, तो यह जगह एक घर जैसी लगती है।"

# Output file
output_file = "cloned_voice2.wav"

# Synthesize
print(tts.languages)
tts.tts(text=text, language='hi', speaker_wav=speaker_wav, file_path=output_file)

print(f"Voice cloned and saved to {output_file}")
