#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
# sdm.py - Assume o chamado do 802.1x, altera o status do chamado e inclue a observação no mesmo, fecha o chamado com a obervação pertinente ao mesmo.
# Autor: Rodrigo Jabur
#
# Uso: import sdm
#
# Histórico:
#	  v1 2016-02-12, Rodrigo Jabur:
#       - Função para logar, acessar o chamado, assumir o chamado e atualizar status com IP e porta do SW e finalizar o chamado no SDM;
#
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
import unittest, time, re, sys, base64


def logarSDM():
    global driver
    ##Variaveis
    url = 'http://seu-server01:8080/CAisd/pdmweb.exe' ##Server produção
    #url = "http://seu-server02:8080/CAisd/pdmweb.exe" ##Server homologação
    user = 'SEU_USER'
    passwd = base64.b64decode('SENHA_BASE64')
    ##Parametros do browser
    profile = FirefoxProfile()
    profile.set_preference("network.proxy.type",0);
    profile.set_preference("browser.download.manager.showWhenStarting", False)
    profile.set_preference("browser.download.folderList", 2);
    profile.set_preference("browser.download.dir", "/tmp/lixo")
    profile.set_preference("browser.download.downloadDir", "/tmp/lixo")
    profile.set_preference("browser.download.defaultFolder", "/tmp/lixo")
    profile.set_preference("browser.helperApps.neverAsk.saveToDisk","application/msword, application/csv, application/ris, text/csv, image/png, application/pdf, text/html, text/plain, application/zip, application/x-zip, application/x-zip-compressed, application/download, application/octet-stream")
    ##Abre o Browser
    driver = webdriver.Firefox(firefox_profile=profile)
    ##Entra na URL
    driver.get(url)
    ##Insere usuario e senha
    driver.find_element_by_id("USERNAME").clear()
    driver.find_element_by_id("USERNAME").send_keys(user)
    driver.find_element_by_id("PIN").clear()
    driver.find_element_by_id("PIN").send_keys(passwd)
    time.sleep(1)
    ##Clica em Logon
    driver.find_element_by_css_selector("#imgBtn0 > span").click()
    time.sleep(6)


def acessarChamado(numChamado):
    ##Variaveis
    chamado=numChamado
    ##Dentro da pagina (window_handles[0]) entre no frame gobtn
    driver.switch_to_frame("gobtn")
    ##Altera a opção default de Incidente para Solicitação
    elemento = driver.find_element_by_id("ticket_type")
    for option in elemento.find_elements_by_tag_name('option'):
        #print option.text
        if option.text == u'Solicitação':
            option.click() # select() in earlier versions of webdriver
            break
    time.sleep(2)
    ##Seleciona o campo de pesquisa, insere o numero do chamado e clica em Ir
    driver.find_element_by_name("searchKey").send_keys(chamado)
    driver.find_element_by_css_selector("#imgBtn0 > span").click()
    time.sleep(3)
    ##Altera para a janela[1] e entra dentro do frame "cai_main" e clca em Editar
    driver.switch_to_window(driver.window_handles[1])
    time.sleep(1)


def assumeChamado(numChamado):
    ##Variaveis
    responsavel = 'Seu Nome no SDM'
    logarSDM()
    acessarChamado(numChamado)
    ##Dentro da pagina (window_handles[1]) entre no frame cai_main e clcia em editar.
    driver.switch_to_frame("cai_main")
    driver.find_element_by_id("imgBtn0").click()
    time.sleep(1)
    ##Limpa o campo "Responsável", insere o nome do usuário, clica no index do SDM com o nome do usuário e fecha a nova janela aberta pelo SDM
    driver.find_element_by_id("df_2_0").clear()
    time.sleep(1)
    driver.find_element_by_id("df_2_0").send_keys(responsavel)
    time.sleep(3)
    #driver.find_element_by_link_text(responsavel).click()
    driver.find_element_by_class_name("ui-menu-item").click()
    time.sleep(1)
    driver.switch_to_window(driver.window_handles[2])
    time.sleep(3)
    driver.switch_to_frame("cai_main")
    driver.find_element_by_id("rslnk_0_0").click()
    #driver.close()
    time.sleep(2)
    ##Seleciona novamente a janela[1] e clica em Salvar
    driver.switch_to_window(driver.window_handles[1])
    driver.switch_to_frame("cai_main")
    driver.find_element_by_id("imgBtn0").click()
    time.sleep(2)
    ##Fecha todo o browser
    driver.quit()


def aguardandoUsuario(numChamado, msgSaida):
    ##Variaveis
    #statusChamado = u'Efetuada a desativação do 802.1X na porta XX do SW: YYY.YYY.YYY.YYY\nAguardando solicitação do técnico para ativação.' #Exemplo de conteúdo da variável
    statusChamado = msgSaida
    logarSDM()
    acessarChamado(numChamado)
    ##Dentro da pagina (window_handles[1]) entre no frame menubar e clica no menu Atividades
    driver.switch_to_frame("menubar")
    driver.find_element_by_id("menu_2").click()
    time.sleep(2)
    ##Altera para o frame cai_main e clica no submenu "Atualizar staus..."
    driver.switch_to_default_content()
    driver.switch_to_frame("cai_main")
    driver.find_element_by_id("amActivities_1").click()
    time.sleep(3)
    ##Seleciona a janela[2], altera para o frame cai_main e muda o status para "Aguardando Usuário"
    driver.switch_to_window(driver.window_handles[2])
    driver.switch_to_frame("cai_main")
    time.sleep(1)
    elemento = driver.find_element_by_id("df_1_1")
    for option in elemento.find_elements_by_tag_name('option'):
        if option.text == u'Aguardando Usuário':
            option.click()
            break
    time.sleep(2)
    ##Escreve no campo log do chamado.
    driver.find_element_by_id("df_3_0").send_keys(statusChamado.decode('utf-8'))
    time.sleep(3)
    ##Clica no botão Salvar
    driver.find_element_by_id("imgBtn0").click()
    time.sleep(1)
    ##Fecha todo o browser
    driver.quit()

    
def resolvido(numChamado):
    ##Variaveis
    statusChamado = u'Efetuada a ativação do 802.1X conforme solicitado.'
        
    logarSDM()
    acessarChamado(numChamado)
    ##Clica em Atividades no menu do SDM
    driver.switch_to_frame("menubar")
    driver.find_element_by_id("menu_2").click()
    time.sleep(2)
    ##Clica em Atualizar status no submenu Atividades
    driver.switch_to_default_content()
    driver.switch_to_frame("cai_main")
    driver.find_element_by_id("amActivities_1").click()
    time.sleep(3)
    ##Seleciona a janela[2], altera para o frame cai_main e muda o status para "Resolvido"
    driver.switch_to_window(driver.window_handles[2])
    driver.switch_to_frame("cai_main")
    time.sleep(1)
    elemento = driver.find_element_by_id("df_1_1")
    for option in elemento.find_elements_by_tag_name('option'):
        if option.text == u'Resolvido':
            option.click()
            break
    time.sleep(2)
    ##Escreve no campo log do chamado.
    driver.find_element_by_id("df_3_0").send_keys(statusChamado)
    time.sleep(3)
    ##Clica no botão Salvar
    driver.find_element_by_id("imgBtn0").click()
    time.sleep(1)
    ##Fecha todo o browser
    driver.quit()


##Testando as funções
#assumeChamado(sys.argv[1])
#resolvido(sys.argv[1])
#aguardandoUsuario(sys.argv[1])
