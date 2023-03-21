
#!/usr/bin/env python3
import os
import subprocess
import PySimpleGUI as sg
import threading
import logging

resolution_16_9 = ["1920x1080", "1280x720", "720x406"]

base_dir = os.path.dirname(os.path.realpath(__file__))

class MainGui:
	
	def __init__(self):
		self.layout = []

		# 入力ファイル名設定
		self.label_in = sg.Text("入力ファイル名")
		self.textbox_in = sg.Input()
		self.button_in = sg.FileBrowse('ファイルを選択', key="input_file_path")
		self.layout.append([self.label_in, self.textbox_in, self.button_in])

		# 出力ファイル名設定
		self.label_out = sg.Text("出力ファイル名")
		self.textbox_out = sg.Input()
		self.button_out = sg.FileBrowse('ファイルを選択', key="output_file_path")
		self.layout.append([self.label_out, self.textbox_out, self.button_out])

		# 解像度
		self.comboRes = [sg.Text("解像度"), sg.Combo(values=resolution_16_9, key="resolution")]
		self.layout.append(self.comboRes)

		# 倍速
		self.input_xpd = [sg.Text("x倍速設定"), sg.Input(key="xspd")]
		self.layout.append(self.input_xpd)

		# 実行ボタン
		self.buttonBTM = sg.Button('実行', key='run')
		self.layout.append([[self.buttonBTM]])

		self.main_window = sg.Window('FFMEPG-GUI', self.layout)
		self.windows = []
		self.windows.append(self.main_window)
			
	def start(self):
		should_exit = False
		while not should_exit:
			for window in self.windows:
				event, values = window.read()

				if event == sg.WIN_CLOSED: #ウィンドウのXボタンを押したときの処理
					window.close()
					if window == self.main_window:
						should_exit = True
				
				if event == "run":
					self.on_buttonBTM_changed(values)
		logging.info("アプリ終了")
	
	def on_buttonBTM_changed(self, values):

		input_file_path = values["input_file_path"]
		output_file_path = values["output_file_path"]

		if output_file_path == "":
			p1 = os.path.dirname(input_file_path)
			p2 = os.path.basename(input_file_path)
			output_file_path = f"{p1}/out_{p2}"
		
		additional_options = []
		if values["resolution"] != "":
			additional_options.extend(["-s", values["resolution"]])
		if values["xspd"] != "":
			try:
				xspd = float(values["xspd"])
				additional_options.extend(["-vf", f"setpts=PTS/{xspd}", "-af", f"atempo={xspd}"])
			except:
				logging.error("無効な倍速値: %s" % values["xspd"])
				return

		# ファイル上書きするか
		if os.path.exists(output_file_path):
			ret = sg.popup_yes_no(f"{output_file_path} は既に存在します。上書きしますか？")
			if ret == "No":
				logging.error("出力ファイル名を変更してください")
				return # 実行しない
			additional_options.extend(["-y"])

		COMMAND = []
		COMMAND.extend(["ffmpeg", "-i", f"\"{input_file_path}\""])
		COMMAND.extend(additional_options)
		COMMAND.extend(["-hide_banner", f"\"{output_file_path}\""])
		
		# スレッドを立ち上げてffmpegコマンド実行
		t = threading.Thread(target=self.RunEncode, args=(COMMAND,))
		t.daemon = True
		t.start()
	
	def RunEncode(self, command_list):
		try:
			cmd = " ".join(command_list)
			logging.info(f"command:\t{cmd}")
			subprocess.run(cmd, shell=True)
			logging.info("エンコード完了")	

		except Exception as e:
			logging.error("変換エラー:", e)

if __name__ == '__main__':
	gui = MainGui()
	gui.start()
