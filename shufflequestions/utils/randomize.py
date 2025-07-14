# your_app/utils/randomize.py
import os
import shutil
import zipfile
import random
import string
import uuid
from datetime import datetime
from threading import Timer
from docx import Document
from docx.shared import Pt
from django.conf import settings
from .timestamp import get_timestamp
from .check_time import delete_time

# # Ensure /public folder exists
# PUBLIC_DIR = os.path.join(settings.BASE_DIR, 'public')
# os.makedirs(PUBLIC_DIR, exist_ok=True)

def shuffle_array(arr):
	shuffled = arr[:]
	random.shuffle(shuffled)
	return shuffled


def generate_alphabets(n):
	return [chr(65 + i) for i in range(n)]  # A, B, C, D...


def schedule_deletion(zip_path, dir_path):
	def delete_files():
		timestamp = get_timestamp()
		try:
			if os.path.exists(zip_path):
				os.remove(zip_path)
				print(f"ZIP file {zip_path} deleted after 5 hours {timestamp}")
			if os.path.exists(dir_path):
				shutil.rmtree(dir_path)
				print(f"Directory {dir_path} deleted after 5 hours {timestamp}")
		except Exception as e:
			print(f"Error in scheduled cleanup {timestamp}: {e}")

	Timer(delete_time, delete_files).start()


def save_docx(paragraphs, file_path):
	doc = Document()
	for para in paragraphs:
		p = doc.add_paragraph(para)
		p.style.font.size = Pt(12)
	doc.save(file_path)


def Randomize(data):
	try:
		# random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
		# variant_id = f"{uuid.uuid4().hex[:8]}_{random_str}"
		# Generate 4 random lowercase alphanumeric characters
		random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))

		# Get current time
		now = datetime.now()
		year = now.year
		month = f"{now.month:02d}"
		date = f"{now.day:02d}"
		hours = f"{now.hour:02d}"
		minutes = f"{now.minute:02d}"
		seconds = f"{now.second:02d}"

		# Combine to form variantId
		variant_id = f"{year}{month}{date}_{hours}{minutes}{seconds}_{random_str}"


		zip_filename = f"studdiebudie_{variant_id}.zip"
		public_dir = os.path.join(settings.BASE_DIR, 'public')
		dir_path = os.path.join(public_dir, variant_id)
		os.makedirs(dir_path, exist_ok=True)
		os.chmod(public_dir, 0o777)
		os.chmod(dir_path, 0o777)

		types = generate_alphabets(int(data['noOfTypes']))

		for i, type_code in enumerate(types):
			questions = shuffle_array(data['postQuestions'])
			answer_key = []

			header_lines = [
				data['school'],
				f"Subject: {data['subject']}",
				f"Class: {data['class']}",
				f"Term: {data['term']}",
				f"Duration: {data['duration']}",
				f"Instruction: {data['instruction']}",
				f"Type: {type_code}",
				""
			]

			question_lines = header_lines[:]
			for idx, q in enumerate(questions):
				opts = shuffle_array([
					{"text": q["correct_answer"], "isCorrect": True},
					{"text": q["wrong_answer1"], "isCorrect": False},
					{"text": q["wrong_answer2"], "isCorrect": False},
					{"text": q["wrong_answer3"], "isCorrect": False},
				])
				for j, opt in enumerate(opts):
					opt['label'] = chr(65 + j)
				correct = next(o for o in opts if o["isCorrect"])
				answer_key.append(f"{idx + 1}. {correct['label']}")

				question_lines.append(f"{idx + 1}. {q['question']}")
				for opt in opts:
					question_lines.append(f"{opt['label']}. {opt['text']}")
				question_lines.append("")

			# Save Question and Answer Files
			quest_dir = os.path.join(dir_path, 'questions')
			ans_dir = os.path.join(dir_path, 'answers')
			os.makedirs(quest_dir, exist_ok=True)
			os.makedirs(ans_dir, exist_ok=True)

			save_docx(question_lines, os.path.join(quest_dir, f"Exam_type_{type_code}.docx"))
			with open(os.path.join(quest_dir, f"Exam_type_{type_code}.txt"), "w") as f:
				f.write("\n".join(question_lines))

			with open(os.path.join(ans_dir, f"Answers_type_{type_code}.txt"), "w") as f:
				f.write("\n".join(answer_key))

		# Zip the directory
		zip_path = os.path.join(public_dir, zip_filename)
		with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as archive:
			for foldername, _, filenames in os.walk(dir_path):
				for filename in filenames:
					file_path = os.path.join(foldername, filename)
					arcname = os.path.relpath(file_path, os.path.join(dir_path, '..'))
					archive.write(file_path, arcname)

		# schedule_deletion(zip_path, dir_path)

		return f"/public/{zip_filename}"

	except Exception as e:
		print(f"Error generating exam bundle: {get_timestamp()} =>", e)
		raise Exception("Failed to generate exam bundle")
