#Steuerung SBR-Anlage Kläranlage Altenahr MB2022-06
#control program for the emergency & temporary wastewater treatment plant in Altenahr, 
#which was installed in April 2022 after the catastrophic flood from Juli 2021.
#This temporary control program ran successfully by a Raspberry Pi Zero WH 
#connected to a LOW-Triggered relais board from May until July 2022.
#With many thanks to Ludwig, Calvin, Kurt and Christoph for their hardware support, 
#the friendly commitment and that tried it with me and this program!

import time
import tkinter
import threading
from datetime import datetime, timedelta
import RPi.GPIO as GPIO

main = tkinter.Tk()
main.geometry('1000x700')
main.title('Steuerung SBR-Anlage Altenahr')

def ende():
    '''Close and End'''
    global hauptlauf, sbr1_lauf
    hauptlauf = "AUS"
    sbr1_lauf = "AUS"
    allout()
    GPIO.cleanup()
    main.destroy()

def tgesberechnen():
    '''calculate total time'''
    global t_d1, t_n1, t_d2, t_n2, t_sed, t_abzug, t_still, t_ges
    t_ges = t_d1 + t_n1 + t_d2 + t_n2 + t_sed + t_abzug + t_still
    ausgabetges["text"] = str(t_ges)

def uebernehmen(phasenzeit, eingabevariable, ausgabevariable,
                fehlermeldungsvariable):
    '''check input'''
    try:
        ganzzahl = int(eingabevariable.get())
        if 0 <= ganzzahl < 1000:
            phasenzeit = ganzzahl
            ausgabevariable["text"] = str(phasenzeit)
        else:
            t_11 = threading.Thread(target = fehlermeldung,
                                   args = (fehlermeldungsvariable,))
            t_11.start()
    except:
        t_11 = threading.Thread(target = fehlermeldung,
                               args = (fehlermeldungsvariable,))
        t_11.start()
    return(phasenzeit)

def fehlermeldung(fehlermeldungsv):
    '''error message'''
    fehlermeldungsv["text"] = "Bitte eine ganze Zahl zwischen 0 und 999 eingeben"
    time.sleep(3)
    fehlermeldungsv["text"] = ""

def deni1get():
    '''get input for Deni1'''
    global t_d1
    t_d1 = uebernehmen(t_d1, eingabe1, ausgabedeni1, fehlerdeni1)
    tgesberechnen()
    eingabe1.delete(0, 'end')

def nitri1get():
    '''get input for Nitri1'''
    global t_n1
    t_n1 = uebernehmen(t_n1, eingabe2, ausgabenitri1, fehlernitri1)
    tgesberechnen()
    eingabe2.delete(0, 'end')

def deni2get():
    '''get input for Deni2'''
    global t_d2
    t_d2 = uebernehmen(t_d2, eingabe3, ausgabedeni2, fehlerdeni2)
    tgesberechnen()
    eingabe3.delete(0, 'end')

def nitri2get():
    '''get input for Nitri2'''
    global t_n2
    t_n2 = uebernehmen(t_n2, eingabe4, ausgabenitri2, fehlernitri2)
    tgesberechnen()
    eingabe4.delete(0, 'end')

def sedget():
    '''get input for Sedimentation'''
    global t_sed
    t_sed = uebernehmen(t_sed, eingabe5, ausgabesed, fehlersed)
    tgesberechnen()
    eingabe5.delete(0, 'end')

def klabzugget():
    '''get input for clarification'''
    global t_abzug
    t_abzug = uebernehmen(t_abzug, eingabe6, ausgabeklabzug, fehlerklabzug)
    tgesberechnen()
    eingabe6.delete(0, 'end')

def stillget():
    '''get input for waiting time'''
    global t_still
    t_still = uebernehmen(t_still, eingabe7, ausgabestillstand,
                          fehlerstillstand)
    tgesberechnen()
    eingabe7.delete(0, 'end')

def GPIO_initialisieren():
    '''initialise GPIOs'''
    GPIO.setmode(GPIO.BCM)

    GPIO.setup(23, GPIO.OUT) #Zulaufpumpe
    GPIO.setup(22, GPIO.OUT) #Ruehrwerk
    GPIO.setup(25, GPIO.OUT) #Beluefter1
    GPIO.setup(24, GPIO.OUT) #Beluefter2

def allout():
    '''set out all GPIOs'''
    GPIO.output(23, GPIO.HIGH) #Ausschalten Zulaufpumpe
    GPIO.output(22, GPIO.HIGH) #Ausschalten Ruehrwerk
    GPIO.output(25, GPIO.HIGH) #Ausschalten Belüfter1
    GPIO.output(24, GPIO.HIGH) #Ausschalten Belüfter2

def countdownSBR1():
    '''calculate and show time until next phase starts'''
    global sbr1_auto, sbr1_phaseendezeit
    while sbr1_auto == "AN":
        while datetime.now() < sbr1_phaseendezeit:
            restzeit = str((sbr1_phaseendezeit - datetime.now()))
            SBR1Restzeitlabel['text'] = restzeit[0:restzeit.find('.')]
            time.sleep(1)
        SBR1Restzeitlabel['text'] = ''

def SBR1an():
    '''run SBR1'''
    global t_d1, t_n1, t_d2, t_n2, t_sed, t_abzug, t_still, sbr1_lauf, sbr1_phaseendezeit, sbr1_auto, sbr1_count
    sbr1_auto = "AN"
    t_5 = threading.Thread(target = countdownSBR1)
    t_5.start()
    while sbr1_lauf == "AN":
        #1. Deniphase 1: Ruehrwerk an
        GPIO.output(22, GPIO.LOW) #Einschalten Ruehrwerk
        sbr1phase["text"] = "Denitrifikation 1"
        sbr1phasestart["text"] = time.strftime("%H:%M:%S",time.localtime())
        sbr1_phaseendezeit = datetime.now()+timedelta(minutes = t_d1)
        sbr1phaseende["text"] = sbr1_phaseendezeit.strftime('%H:%M:%S')
        while datetime.now() < sbr1_phaseendezeit and sbr1_lauf == "AN":
            time.sleep(1)

        #2. Nitriphase 1: Beluefter an
        GPIO.output(25, GPIO.LOW) #Einschalten Belüfter1
        GPIO.output(24, GPIO.LOW) #Einschalten Belüfter2
        sbr1phase["text"] = "Nitrifikation 1"
        sbr1phasestart["text"] = time.strftime("%H:%M:%S",time.localtime())
        sbr1_phaseendezeit = datetime.now()+timedelta(minutes = t_n1)
        sbr1phaseende["text"] = sbr1_phaseendezeit.strftime('%H:%M:%S')
        while datetime.now() < sbr1_phaseendezeit and sbr1_lauf == "AN":
            time.sleep(1)

        #3. Deniphase 2: Beluefter aus
        GPIO.output(25, GPIO.HIGH) #Ausschalten Belüfter1
        GPIO.output(24, GPIO.HIGH) #Ausschalten Belüfter2
        sbr1phase["text"] = "Denitrifikation 2"
        sbr1phasestart["text"] = time.strftime("%H:%M:%S",time.localtime())
        sbr1_phaseendezeit = datetime.now()+timedelta(minutes = t_d2)
        sbr1phaseende["text"] = sbr1_phaseendezeit.strftime('%H:%M:%S')
        while datetime.now() < sbr1_phaseendezeit and sbr1_lauf == "AN":
            time.sleep(1)

        #4. Nitriphase 2: Beluefter an
        GPIO.output(25, GPIO.LOW) #Einschalten Belüfter1
        GPIO.output(24, GPIO.LOW) #Einschalten Belüfter2
        sbr1phase["text"] = "Nitrifikation 2"
        sbr1phasestart["text"] = time.strftime("%H:%M:%S",time.localtime())
        sbr1_phaseendezeit = datetime.now()+timedelta(minutes = t_n2)
        sbr1phaseende["text"] = sbr1_phaseendezeit.strftime('%H:%M:%S')
        while datetime.now() < sbr1_phaseendezeit and sbr1_lauf == "AN":
            time.sleep(1)

        #5. Sedimentations-/Absetzphase: Ruehrwerk und Belüfter aus
        GPIO.output(22, GPIO.HIGH) #Ausschalten Ruehrwerk
        GPIO.output(25, GPIO.HIGH) #Ausschalten Belüfter1
        GPIO.output(24, GPIO.HIGH) #Ausschalten Belüfter2
        sbr1phase["text"] = "Sedimentation"
        sbr1phasestart["text"] = time.strftime("%H:%M:%S",time.localtime())
        sbr1_phaseendezeit = datetime.now()+timedelta(minutes = t_sed)
        sbr1phaseende["text"] = sbr1_phaseendezeit.strftime('%H:%M:%S')
        while datetime.now() < sbr1_phaseendezeit and sbr1_lauf == "AN":
            time.sleep(1)

        #7. Klarwasserabzugs- und Zulaufphase
        GPIO.output(23, GPIO.LOW) #Einschalten Zulaufpumpe
        sbr1phase["text"] = "Klarwasserabzug, Zulauf"
        sbr1phasestart["text"] = time.strftime("%H:%M:%S",time.localtime())
        sbr1_phaseendezeit = datetime.now()+timedelta(minutes = t_abzug)
        sbr1phaseende["text"] = sbr1_phaseendezeit.strftime('%H:%M:%S')
        while datetime.now() < sbr1_phaseendezeit and sbr1_lauf == "AN":
            time.sleep(1)
        GPIO.output(23, GPIO.HIGH) #Ausschalten Zulaufpumpe

        #9. Stillstandszeit
        sbr1phase["text"] = "Stillstandszeit"
        sbr1phasestart["text"] = time.strftime("%H:%M:%S",time.localtime())
        sbr1_phaseendezeit = datetime.now()+timedelta(minutes = t_still)
        sbr1phaseende["text"] = sbr1_phaseendezeit.strftime('%H:%M:%S')
        while datetime.now() < sbr1_phaseendezeit and sbr1_lauf == "AN":
            time.sleep(1)

        if sbr1_lauf == "AN":
            sbr1_count += 1
        SBR1Durchganglabel["text"] = str(sbr1_count)

    sbr1phase["text"] = "Pause"
    sbr1_phaseendezeit = datetime.now()
    sbr1phaseende["text"] = sbr1_phaseendezeit.strftime('%H:%M:%S')
    sbr1phasestart["text"] = ""
    sbr1_auto = "AUS"

def schalten1():
    '''put SBR1 on or off'''
    global sbr1_lauf
    if sbr1_lauf == "AUS" and sbr1phase["text"] == "Pause":
        sbr1_lauf = "AN"
        schalter1['bg'] = 'lime'
        schalter1['text'] = 'An'
        t_1 = threading.Thread(target = SBR1an)
        t_1.start()
    else:
        sbr1_lauf = "AUS"
        schalter1['bg'] = 'red'
        schalter1['text'] = 'Aus'

def zeitstempelaktualisieren():
    '''update time stamp'''
    global hauptlauf
    while hauptlauf == "AN":
        zeitjetzt['text'] = time.strftime("%H:%M:%S",time.localtime())
        time.sleep(1)

def cputempaktualisieren():
    '''update temperatur for CPU'''
    global hauptlauf
    while hauptlauf == "AN":
        tempData = "/sys/class/thermal/thermal_zone0/temp"
        dateilesen = open(tempData, "r")
        temperatur = dateilesen.readline(5)
        dateilesen.close()
        temperatur = round(float(temperatur)/1000,1)
        cputemp['text'] = temperatur
        time.sleep(10)

#Programm Start
GPIO_initialisieren()
allout()
hauptlauf = "AN"
sbr1_lauf = "AN"
sbr1_auto = "AUS"
t_d1 = 0#30 #Min
t_n1 = 240#210 #Min
t_d2 = 0 #Min
t_n2 = 0 #Min
t_sed = 30#60 #Min
t_abzug = 5#60 #Min
t_still = 15#30 Min
t_ges = t_d1 + t_n1 + t_d2 + t_n2 + t_sed + t_abzug + t_still
sbr1_count = 0
sbr1_phaseendezeit = datetime.now()

#Überschrift
tkinter.Label(main, text = 'Kläranlage Altenahr ', font = ('arial', 11,'bold')
              ).place(x = 10, y = 10)
tkinter.Label(main, text = 'SBR ', font = ('arial', 20, 'bold')
              ).place(x = 10, y = 50, anchor = 'w')
tkinter.Label(main, text = '1', font = ('arial', 20, 'bold')
              ).place(x = 250, y = 50, anchor = 'center')

#Schalter
schalter1 = tkinter.Button(main, width = 8, text = 'Schalten',
                           command = schalten1, cursor = 'tcross', bg = 'lime',
                           font = ('arial', 10, 'bold'))
schalter1.place(x = 250, y = 85, anchor = 'center')

#Phase
tkinter.Label(main, text = 'Aktuelle Phase:', font = ('arial', 11, 'bold')
              ).place(x = 10, y = 120, anchor = 'w')
sbr1phase = tkinter.Label(main, text = 'Pause', font = ('arial', 11, 'bold'))
sbr1phase.place(x = 250, y = 120, anchor = 'center')

tkinter.Label(main, text = 'Start Phase:', font = ('arial', 11, 'bold')
              ).place(x = 10, y = 140, anchor = 'w')
sbr1phasestart = tkinter.Label(main, text = '-', font = ('arial', 11, 'bold'))
sbr1phasestart.place(x = 250, y = 140, anchor = 'center')

tkinter.Label(main, text = 'Ende Phase:', font = ('arial', 11, 'bold')
              ).place(x = 10, y = 160, anchor = 'w')
sbr1phaseende = tkinter.Label(main, text = '-',  font = ('arial', 11, 'bold'))
sbr1phaseende.place(x = 250, y = 160, anchor = 'center')

tkinter.Label(main, text = 'Restzeit:', font = ('arial', 11, 'bold')
              ).place(x = 10, y = 180, anchor = 'w')
SBR1Restzeitlabel = tkinter.Label(main, text = '-',
                                  font = ('arial', 11, 'bold'))
SBR1Restzeitlabel.place(x = 250, y = 180, anchor = 'center')

tkinter.Label(main, text = 'Durchgang:', font = ('arial', 11, 'bold')
              ).place(x = 10, y = 200, anchor = 'w')
SBR1Durchganglabel = tkinter.Label(main, text = str(sbr1_count),
                                   font = ('arial', 11, 'bold'))
SBR1Durchganglabel.place(x = 250, y = 200, anchor = 'center')

#Deni1
tkinter.Label(main, text = 'Denitrifikation 1: ', font = ('arial', 11, 'bold')
              ).place(x = 150, y = 250, anchor = 'e')
ausgabedeni1 = tkinter.Label(main, text = str(t_d1),
                             font = ('arial', 11, 'bold'))
ausgabedeni1.place(x = 245, y = 240, anchor = 'e')
tkinter.Label(main, text = 'Min.', font = ('arial', 11, 'bold')
              ).place(x = 250, y = 240, anchor = 'w')
eingabe1 = tkinter.Entry(main, width = 5)
eingabe1.place(x = 245, y = 260, anchor = 'e')
eingabe1but = tkinter.Button(main, text = "OK", font = ('arial', 8, 'bold'),
                             width = 1, command = deni1get)
eingabe1but.place(x = 250, y = 260, anchor = 'w')
fehlerdeni1 = tkinter.Label(main, font = ('arial', 11, 'bold'), fg = 'red')
fehlerdeni1.place(x = 160, y = 260, anchor = 'w')

#Nitri1
tkinter.Label(main, text = 'Nitrifikation 1: ', font = ('arial', 11, 'bold')
              ).place(x = 150, y = 310, anchor = 'e')
ausgabenitri1 = tkinter.Label(main, text = str(t_n1)
                              , font = ('arial', 11, 'bold'))
ausgabenitri1.place(x = 245, y = 300, anchor = 'e')
tkinter.Label(main, text = 'Min.', font = ('arial', 11, 'bold')
              ).place(x = 250, y = 300, anchor = 'w')
eingabe2 = tkinter.Entry(main, width = 5)
eingabe2.place(x = 245, y = 320, anchor = 'e')
eingabe2but = tkinter.Button(main, text = "OK", font = ('arial', 8, 'bold'),
                             width = 1, command = nitri1get)
eingabe2but.place(x = 250, y = 320, anchor = 'w')
fehlernitri1 = tkinter.Label(main, font = ('arial', 11, 'bold'), fg = 'red')
fehlernitri1.place(x = 160, y = 320, anchor = 'w')

#Deni2
tkinter.Label(main, text = 'Denitrifikation 2: ', font = ('arial', 11, 'bold')
              ).place(x = 150, y = 370, anchor = 'e')
ausgabedeni2 = tkinter.Label(main, text = str(t_d2),
                             font = ('arial', 11, 'bold'))
ausgabedeni2.place(x = 245, y = 360, anchor = 'e')
tkinter.Label(main, text = 'Min.', font = ('arial', 11, 'bold')
              ).place(x = 250, y = 360, anchor = 'w')
eingabe3 = tkinter.Entry(main, width = 5)
eingabe3.place(x = 245, y = 380, anchor = 'e')
eingabe3but = tkinter.Button(main, text = "OK", font = ('arial', 8, 'bold'),
                             width = 1, command = deni2get)
eingabe3but.place(x = 250, y = 380, anchor = 'w')
fehlerdeni2 = tkinter.Label(main, font = ('arial', 11, 'bold'), fg = 'red')
fehlerdeni2.place(x = 160, y = 380, anchor = 'w')

#Nitri2
tkinter.Label(main, text = 'Nitrifikation 2: ', font = ('arial', 11, 'bold')
              ).place(x = 150, y = 430, anchor = 'e')
ausgabenitri2 = tkinter.Label(main, text = str(t_n2),
                              font = ('arial', 11, 'bold'))
ausgabenitri2.place(x = 245, y = 420, anchor = 'e')
tkinter.Label(main, text = 'Min.', font = ('arial', 11, 'bold')
              ).place(x = 250, y = 420, anchor = 'w')
eingabe4 = tkinter.Entry(main, width = 5)
eingabe4.place(x = 245, y = 440, anchor = 'e')
eingabe4but = tkinter.Button(main, text = "OK", font = ('arial', 8, 'bold'),
                             width = 1, command = nitri2get)
eingabe4but.place(x = 250, y = 440, anchor = 'w')
fehlernitri2 = tkinter.Label(main, font = ('arial', 11, 'bold'), fg = 'red')
fehlernitri2.place(x = 160, y = 440, anchor = 'w')

#Absetz-/Sedimentation
tkinter.Label(main, text = 'Sedimentation: ', font = ('arial', 11, 'bold')
              ).place(x = 150, y = 500, anchor = 'e')
ausgabesed = tkinter.Label(main, text = str(t_sed), font = ('arial', 11,
                                                            'bold'))
ausgabesed.place(x = 245, y = 490, anchor = 'e')
tkinter.Label(main, text = 'Min.', font = ('arial', 11, 'bold')
              ).place(x = 250, y = 490, anchor = 'w')
eingabe5 = tkinter.Entry(main, width = 5)
eingabe5.place(x = 245, y = 510, anchor = 'e')
eingabe5but = tkinter.Button(main, text = "OK", font = ('arial', 8, 'bold'),
                             width = 1, command = sedget)
eingabe5but.place(x = 250, y = 510, anchor = 'w')
fehlersed = tkinter.Label(main, font = ('arial', 11, 'bold'), fg = 'red')
fehlersed.place(x = 160, y = 510, anchor = 'w')

#Klarwasserabzug, Zulauf
tkinter.Label(main, text = 'Klarwasserabzug: ', font = ('arial', 11, 'bold')
              ).place(x = 150, y = 560, anchor = 'e')
ausgabeklabzug = tkinter.Label(main, text = str(t_abzug),
                               font = ('arial', 11, 'bold'))
ausgabeklabzug.place(x = 245, y = 550, anchor = 'e')
tkinter.Label(main, text = 'Min.', font = ('arial', 11, 'bold')
              ).place(x = 250, y = 550, anchor = 'w')
eingabe6 = tkinter.Entry(main, width = 5)
eingabe6.place(x = 245, y = 570, anchor = 'e')
eingabe6but = tkinter.Button(main, text = "OK", font = ('arial', 8, 'bold'),
                             width = 1, command = klabzugget)
eingabe6but.place(x = 250, y = 570, anchor = 'w')
fehlerklabzug = tkinter.Label(main, font = ('arial', 11, 'bold'), fg = 'red')
fehlerklabzug.place(x = 160, y = 570, anchor = 'w')

#Stillstandszeit
tkinter.Label(main, text = 'Stillstandszeit: ', font = ('arial', 11, 'bold')
              ).place(x = 150, y = 620, anchor = 'e')
ausgabestillstand = tkinter.Label(main, text = str(t_still),
                                  font = ('arial', 11, 'bold'))
ausgabestillstand.place(x = 245, y = 610, anchor = 'e')
tkinter.Label(main, text = 'Min.', font = ('arial', 11, 'bold')
              ).place(x = 250, y = 610, anchor = 'w')
eingabe7 = tkinter.Entry(main, width = 5)
eingabe7.place(x = 245, y = 630, anchor = 'e')
eingabe7but = tkinter.Button(main, text = "OK", font = ('arial', 8, 'bold'),
                             width = 1, command = stillget)
eingabe7but.place(x = 250, y = 630, anchor = 'w')
fehlerstillstand = tkinter.Label(main, font = ('arial', 11, 'bold'), fg = 'red')
fehlerstillstand.place(x = 160, y = 630, anchor = 'w')

#Zyklus/ Gesamtzeit
tkinter.Label(main, text = 'Zykluszeit: ', font = ('arial', 11, 'bold')
              ).place(x = 150, y = 670, anchor = 'e')
ausgabetges = tkinter.Label(main, text = str(t_ges), font = ('arial', 11, 'bold'))
ausgabetges.place(x = 245, y = 670, anchor = 'e')
tkinter.Label(main, text = 'Min.', font = ('arial', 11, 'bold')
              ).place(x = 250, y = 670, anchor = 'w')

#Zeitstempel anzeigen und aktualisieren
zeitjetzt = tkinter.Label(main, text = '-', font = ('arial', 11, 'bold'))
zeitjetzt.place(x = 625, y = 50, anchor = 'w')
threading.Thread(target = zeitstempelaktualisieren).start()

#bei Programmstart SBR-Steuerung anschalten
threading.Thread(target = SBR1an).start()

#CPU-Temperatur anzeigen und aktualisieren
tkinter.Label(main, text = 'CPU-Temp.: ', font = ('arial', 11, 'bold')
              ).place (x = 625, y = 70, anchor = 'w')
tkinter.Label(main, text = '°C', font = ('arial', 11, 'bold')
              ).place (x = 750, y = 70, anchor = 'w')
cputemp = tkinter.Label(main, text = '-', font = ('arial', 11, 'bold'))
cputemp.place(x = 750, y = 70, anchor = 'e')
threading.Thread(target = cputempaktualisieren).start()

#Beenden-Schalter anordnen
endeschalt = tkinter.Button(main, text = 'Beenden', command = ende,
                           cursor = 'tcross', bg= 'white',
                           font = ('arial', 11, 'bold'))
endeschalt.place(x = 625, y = 20, anchor = 'w')

# Programm auch beenden wenn das Fenster geschlossen wird
main.protocol("WM_DELETE_WINDOW", ende)

#loop
main.mainloop()
