# -*- coding: utf-8 -*-

# O objetivo desse programa eh, a partir do arquivo de tweets fornecido pelo proprio twitter,
# fornecer uma ferramenta de busca e filtragem dos links dos tweets, com opcoes de aberturas automáticas
# para acesso a pagina de um tweet específico.

# a funcao all_tweets_from_csv importa os tweets do arquivo csv uma vez fornecido pelo Twitter.
# talvez eventualmente ainda precise de uma adaptação para importar os dados de arquivos js/json
# a funcao retira todos os retweets e deixa apenas os tweets originais do usuario repassado, exportando
# para um outro arquivo csv o resultado.
# Entada: username do twitter + arquivo 'tweets.csv'
# Saida: arquivo 'mytweets.csv'

# a funcao filter_tweets pega os links de tweets pré-filtrados por outra funcao e testa pra ver
# quais ainda existem (e nao foram excluidos), exportando-os para um outro arquivo csv myvalidtweets
# Entrada: arquivo 'mytweets.csv'
# Saida: arquivo 'myvalidtweets.csv'

# a funcao delete_tweets abre os tweets usando o selenium e exclui um a um
# eh possivel otimiza-la em relacao aos tempos entre as diferentes tarefas
# executadas.
# Entrada: username e senha do twitter.
# Saida: arquivo tweets_to_be_reprocessed com links de tweets que deram erro.

# a funcao all_tweets_from_js importa os tweets do arquivo JS fornecido atualmente (Jul/2019) pelo Twitter.
# a funcao retira todos os retweets e deixa apenas os tweets originais do usuario repassado, exportando
# para um arquivo csv o resultado.
# Entrada: username do twitter + arquivo 'tweet.js'
# Saida: arquivo 'mytweets.csv'

import sys
import csv
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import webbrowser
import time
import requests
import json
# from urllib import parse # for separating path and hostname

selenium_time_window = 10;

def start_safari():
	try:
		safari = webdriver.Safari(executable_path = '/usr/bin/safaridriver');
	except selenium.common.exceptions.SessionNotCreatedException:
		print ("Feche a atual sessão e pressione enter para continuar...");
		raw_input();
		return;
	except 'selenium.common.exceptions.SessionNotCreatedException':
		print ("Timeout.");
		return;
	return safari

def login(safari, username, password):
	# filling username
	#TODO: test login success
	safari.get('https://twitter.com/login');
	login_field = WebDriverWait(safari, selenium_time_window).until(EC.presence_of_element_located((By.CLASS_NAME, "js-username-field")));
	login_field.clear();
	login_field.send_keys(username);
	time.sleep(1);	# Wait 1sec

	# filling password
	password_field = WebDriverWait(safari, selenium_time_window).until(EC.presence_of_element_located((By.CLASS_NAME, "js-password-field")));
	password_field.clear();
	password_field.send_keys(password);

	# submit credentials
	password_field.submit()
	time.sleep(selenium_time_window/2);

def all_tweets_from_csv(username):
	mytweets = [];
	with open('tweets.csv') as csvfile:
		spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')

		for row in spamreader:
			if row[6]=='':
				mytweets.append(row);

	with open('mytweets.csv', 'w') as csvfile:
		for tweet_info in mytweets:
			csvfile.write("http://twitter.com/"+username+"/status/"+tweet_info[0]+'\n')

def filter_tweets():
	# my_valid_tweets = []
	with open('mytweets.csv') as arq_read, open('myvalidtweets.csv', 'w') as arq_write:
		count_total = 0;
		count_valid = 0;
		count_unknown = 0;
		for tweet_link in arq_read:
			count_total += 1;
			try:
				r = requests.get(tweet_link.replace('\n',''))
				if "Sorry, that page doesn’t exist!" in r.content:
					print (str(count_total)+": Tweet invalido!")
					pass;
				else:
					count_valid+=1;
					arq_write.write(tweet_link)
					print (str(count_total)+": Tweet valido!");
			except:
				count_unknown+=1;
				print (str(count_total)+": Status indeterminado.");
				arq_write.write(tweet_link);
				# print ("Erro abrindo o tweet");
		print ("\nTotal de tweets processados: " + str(count_total));
		print ("Total de tweets válidos: " + str(count_valid));
		print ("Total de tweets que não puderam ser verificados: " + str(count_unknown));

def open_valid_tweets():
	#TODO: melhorar personalização das opções aqui.
	with open('myvalidtweets.csv') as arq:
		count = 1;
		for tweet_link in arq:
			webbrowser.open(tweet_link.replace('\n',''))
			count+=1;
			if(count % 15 == 0):
				time.sleep(60);
			if (count >= 150):
				break;

def delete_tweets(username, password):
	#TODO: Fazer um arquivo de reprocessamento para exportar os tweets ainda não
	# deletados.

	#TODO: treat rate limited
	#TODO: retry open page when MORE button is not found.
	safari = start_safari();

	if safari == None: 		# Error handling
		return
	login (safari, username, password);
	# try:
	# 	login (safari, username, password);
	# except:
	# 	safari.close();
	# link_reproccess=[];
	with open('myvalidtweets.csv') as arq_read, open('tweets_to_be_reprocessed.csv', 'w') as arq_write:
		for tweet_link in arq_read:
			try:
				safari.get(tweet_link.replace('\n', ''))
				# time.sleep(selenium_time_window);
			except (selenium.common.exceptions.InvalidSessionIdException, selenium.common.exceptions.TimeoutException) as exception_timeout:
				print ("Timeout. Fazer exclusão manual.");
				arq_write.write(tweet_link);
				# print (tweet_link[(tweet_link.find('status/')+len('status/')):])
				raw_input("Pressione enter para continuar...");
				safari.quit()
				safari = start_safari();
				continue
			try:
				more_button = WebDriverWait(safari, selenium_time_window).until(EC.element_to_be_clickable((By.CLASS_NAME, 'r-4qtqp9 r-yyyyoo r-ip8ujx r-dnmrzs r-bnwqim r-1plcrui r-lrvibr r-27tl0q'.replace(' ',"."))));
				# more_button = safari.find_element_by_class_name('r-4qtqp9 r-yyyyoo r-ip8ujx r-dnmrzs r-bnwqim r-1plcrui r-lrvibr r-27tl0q'.replace(' ',"."))
				more_button.click();
				# time.sleep(selenium_time_window);
			except selenium.common.exceptions.TimeoutException:
				# Tentou achar o botão MORE, não conseguiu.
				# Tentar achar "Sorry, not found na pag."
				#TODO: Se tiver um "Something went wrong" ou "Try again" ou "rate limited" na pagina, fazer um sleep de 2min
				try:
					WebDriverWait(safari, selenium_time_window).until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(),'Sorry, that page doesn’t exist!')]")));
					# print ("Tweet invalido.");
					continue;
				except selenium.common.exceptions.TimeoutException:
					try:
						WebDriverWait(safari, selenium_time_window).until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(),'This Tweet is unavailable')]")));
						continue;
					except selenium.common.exceptions.TimeoutException:
						# Recarregar pagina e tentar achar de novo o botao MORE.
						safari.get(tweet_link.replace('\n',''));
						more_button = WebDriverWait(safari, selenium_time_window).until(EC.element_to_be_clickable((By.CLASS_NAME, 'r-4qtqp9 r-yyyyoo r-ip8ujx r-dnmrzs r-bnwqim r-1plcrui r-lrvibr r-27tl0q'.replace(' ',"."))));
						more_button.click();
					except:
						print ("Botão MORE não encontrado. Fazer exclusão manual.");
						# print (tweet_link[(tweet_link.find('status/')+len('status/')):])
						arq_write.write(tweet_link);
						continue;
			except:
				print ("Erro desconhecido: Botão MORE.")
				# print (tweet_link[(tweet_link.find('status/')+len('status/')):])
				# link_reproccess.append(tweet_link);
				arq_write.write(tweet_link)
				continue;

			try:
				# delete_button = safari.find_element_by_class_name('r-daml9f r-4qtqp9'.replace(' ', '.'))
				delete_button = WebDriverWait(safari, selenium_time_window).until(EC.element_to_be_clickable((By.CLASS_NAME, 'r-daml9f r-4qtqp9'.replace(' ',"."))));
				delete_button.click();
				# time.sleep(selenium_time_window);
			except selenium.common.exceptions.NoSuchElementException:
				print ("Botão DELETE não encontrado. Fazer exclusão manual.");
				# print (tweet_link[(tweet_link.find('status/')+len('status/')):])
				# link_reproccess.append(tweet_link);
				arq_write.write(tweet_link);
				continue;
			except:
				print ("Erro desconhecido: Botão DELETE.");
				# print (tweet_link[(tweet_link.find('status/')+len('status/')):])
				# link_reproccess.append(tweet_link);
				arq_write.write(tweet_link);
				continue;

			try:
				delete_confirm = WebDriverWait(safari, selenium_time_window).until(EC.element_to_be_clickable((By.CLASS_NAME, 'css-18t94o4 css-1dbjc4n r-1dgebii r-42olwf r-sdzlij r-1phboty r-rs99b7 r-16y2uox r-1w2pmg'.replace(' ',"."))));
				# delete_confirm = safari.find_element_by_class_name('css-18t94o4 css-1dbjc4n r-1dgebii r-42olwf r-sdzlij r-1phboty r-rs99b7 r-16y2uox r-1w2pmg'.replace(' ','.'))
				delete_confirm.click();
				time.sleep(0.5);
			except selenium.common.exceptions.NoSuchElementException:
				print ("Botão CONFIRM DELETE não encontrado. Fazer exclusão manual.");
				# print (tweet_link[(tweet_link.find('status/')+len('status/')):])
				# link_reproccess.append(tweet_link);
				arq_write.write(tweet_link);
				continue;
			except:
				print ("Erro desconhecido: Botão CONFIRM DELETE.");
				# print (tweet_link[(tweet_link.find('status/')+len('status/')):])
				# link_reproccess.append(tweet_link);
				arq_write.write(tweet_link);
				continue;
	safari.quit();

def all_tweets_from_js(username):
	with open('tweet.js', 'r') as arq_read, open('tweets.json', 'w') as arq_write:
		line = arq_read.readline();
		arq_write.write('[ {')
		line = arq_read.readline();
		while(line):
			arq_write.write(line);
			line = arq_read.readline();

	with open('tweets.json', 'r') as arq_read, open('mytweets.csv', 'w') as arq_tweets, open('retweets.csv', 'w') as arq_retweets:
		tweets = json.load(arq_read);
		for tweet in tweets:
			if int(tweet["created_at"][-4:])<2019:
				if (tweet["full_text"][:4]=="RT @"):
					if tweet["full_text"].find(":")>0:
						arq_retweets.write("http://twitter.com/"+tweet["full_text"][4:(tweet["full_text"].find(":"))].encode('ascii', 'ignore').decode('ascii')+"/status/"+tweet["id"]+"\n");
					else:
						# print (tweet["full_text"][4:].encode('ascii', 'ignore').decode('ascii'))
						#TODO: Consertar essa linha
						arq_retweets.write("http://twitter.com/"+tweet["full_text"][4:][:(tweet["full_text"][4:].find(" "))].encode('ascii', 'ignore').decode('ascii')+"/status/"+tweet["id"]+"\n");
				else:
					arq_tweets.write("http://twitter.com/"+username+"/status/"+tweet["id"]+"\n");

def menu():
	opt = 0;
	while (opt!=6):
		print ("Escolha uma opcao:");
		print ("1. Separar tweets de um arquivo CSV");
		print ("2. Filtrar tweets válidos");
		print ("3. Abrir tweets válidos;");
		print ("4. Deletar tweets válidos")
		print ("5. Separar tweets de um arquivo JS")
		print ("6. Sair");
		try:
			opt = int(sys.argv[1]);
			sys.argv.pop()
			print (opt);
		except:
			opt = int(input());
		if (opt==1):
			pass;
		elif (opt==2):
			filter_tweets();
			pass;
		elif (opt==3):
			open_valid_tweets();
			pass;
		elif (opt==4):
			delete_tweets(twitter_username, twitter_password);
			pass;
		elif (opt==5):
			all_tweets_from_js(twitter_username);
			pass;
		elif (opt!=6):
			print ("Opcao invalida!");

twitter_username = 'samuels15'
twitter_password = 'twt_psswrd'
menu();
