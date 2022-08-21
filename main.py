import util
import logging
from tkinter import *
from tkinter import messagebox
from tkinter.colorchooser import askcolor
from pyglet import font
import tkinter.font as TkFont
from auth import *
from PIL import Image, ImageTk
from requests import get
from webbrowser import open_new
from datetime import datetime
from traceback import print_exc
from cryptocode import encrypt, decrypt
from configparser import ConfigParser


### DEFINITIONS ###
# hyperlink() opens a link via a hyperlink
def hyperlink(url):
    open_new(url)


# updateSelectedCommand() updates which command button is highlighted and displays the arguments needed before submitting
def updateSelectedCommand(cmd):
    global args_list
    global selected_command
    global main_menu
    selected_command = cmd
    darker = util.colorDarken(PURPLE)
    darker = darker.upper()
    # Gets the UI ready for rank command
    if cmd == 1:
        main_menu[1]['bg'] = darker
        main_menu[2]['bg'] = PURPLE
        main_menu[3]['bg'] = PURPLE
        main_menu[4]['bg'] = PURPLE
        main_menu[5]['bg'] = PURPLE
        main_menu[8]['bg'] = PURPLE
        resetArguments()
        args_list.clear()
        name_entry = Entry(window, font=("Orbitron", 20), fg=BLACK, bg=PURPLE, width=12)
        args_list.append(name_entry)
        var = StringVar(window)
        temp = ['na', 'eu', 'ap', 'kr']
        var.set(temp[0])
        args_list.append(var)
        region_select = OptionMenu(window, var, *temp)
        region_select.config(bg=PURPLE, font=("Orbitron", 12), highlightthickness=0)
        args_list.append(region_select)
        temp.clear()
        temp.append('current')
        for i in actsDictionary:
            temp.append(i)
        var1 = StringVar(window)
        var1.set(temp[0])
        args_list.append(var1)
        act_select = OptionMenu(window, var1, *temp)
        act_select.config(bg=PURPLE, font=("Orbitron", 12), highlightthickness=0)
        args_list.append(act_select)
        name_label = Label(window, text="Name#Tag:", font=("Orbitron", 12), bg=PURPLE)
        region_label = Label(window, text="Region:", font=("Orbitron", 12), bg=PURPLE)
        act_label = Label(window, text="Act:", font=("Orbitron", 12), bg=PURPLE)
        args_list.append(name_label)
        args_list.append(region_label)
        args_list.append(act_label)
        args_list[0].place(x=190, y=370)
        args_list[2].place(x=500, y=371)
        args_list[4].place(x=590, y=371)
        args_list[5].place(x=190, y=340)
        args_list[6].place(x=495, y=341)
        args_list[7].place(x=590, y=341)
    if cmd == 2:
        main_menu[2]['bg'] = darker
        main_menu[1]['bg'] = PURPLE
        main_menu[3]['bg'] = PURPLE
        main_menu[4]['bg'] = PURPLE
        main_menu[5]['bg'] = PURPLE
        main_menu[8]['bg'] = PURPLE
        resetArguments()
        args_list.clear()
    if cmd == 3:
        main_menu[3]['bg'] = darker
        main_menu[2]['bg'] = PURPLE
        main_menu[1]['bg'] = PURPLE
        main_menu[4]['bg'] = PURPLE
        main_menu[5]['bg'] = PURPLE
        main_menu[8]['bg'] = PURPLE
        resetArguments()
        args_list.clear()
    if cmd == 4:
        main_menu[4]['bg'] = darker
        main_menu[2]['bg'] = PURPLE
        main_menu[3]['bg'] = PURPLE
        main_menu[1]['bg'] = PURPLE
        main_menu[5]['bg'] = PURPLE
        main_menu[8]['bg'] = PURPLE
        resetArguments()
        args_list.clear()
    if cmd == 5:
        main_menu[5]['bg'] = darker
        main_menu[2]['bg'] = PURPLE
        main_menu[3]['bg'] = PURPLE
        main_menu[4]['bg'] = PURPLE
        main_menu[1]['bg'] = PURPLE
        main_menu[8]['bg'] = PURPLE
        resetArguments()
        args_list.clear()
    if cmd == 6:
        main_menu[8]['bg'] = darker
        main_menu[2]['bg'] = PURPLE
        main_menu[3]['bg'] = PURPLE
        main_menu[4]['bg'] = PURPLE
        main_menu[1]['bg'] = PURPLE
        main_menu[5]['bg'] = PURPLE
        resetArguments()
        args_list.clear()


# resetArguments() deletes all argument displays on the gui
def resetArguments():
    global args_list
    main_menu[7]['text'] = ""
    for i in range(len(args_list)):
        try:
            args_list[i].destroy()
        except AttributeError as e:
            pass


# clears the ui from the main menu elements
def destroyMainMenu():
    for i in range(len(main_menu)):
        main_menu[i].destroy()
    main_menu.clear()


# executes selected command
def submitCommand():
    # selected_command being -1 signals its time for main menu to come back
    global selected_command
    if selected_command == 0:
        main_menu[7]['text'] = "No command selected!"
    else:
        if selected_command == 1:
            player = args_list[0].get()
            region = args_list[1].get()
            act = args_list[3].get()
            temp = util.indexOf(player, "#")
            #checks to see if the name#tag is valid
            if temp == -1:
                main_menu[7]['text'] = "Missing tagline!"
                return
            else:
                player_name = player[0:temp]
                player_tag = player[temp+1:]
                destroyMainMenu()
            #gets rid of arguments elements
            for i in range(len(args_list)):
                try:
                    args_list[i].destroy()
                except AttributeError:
                    pass
            args_list.clear()
            displayRankMenu(player_name, player_tag, region, act)
            selected_command = -1
            return
        elif selected_command == 2:
            selected_command = -1
            destroyMainMenu()
            displayStore()
            return
        elif selected_command == 3:
            selected_command = -1
            destroyMainMenu()
            displayMatchStats()
            return
        elif selected_command == 4:
            selected_command = -1
            destroyMainMenu()
            displayMatchSkins()
            return
        elif selected_command == 5:
            selected_command = -1
            destroyMainMenu()
            displayLogout()
            return
        elif selected_command == 6:
            selected_command = -1
            destroyMainMenu()
            displayHelp()
            return
        else:
            for i in range(len(current_menu)):
                current_menu[i].destroy()
            current_menu.clear()
            displayMainMenu()


# gets user from settings to main menu
def settingToMain():
    for i in range(len(current_menu)):
        current_menu[i].destroy()
    current_menu.clear()
    displayMainMenu()


# changes colors to users choice
def customizeColors():
    global BLACK
    global PURPLE
    bgChange = messagebox.askyesno("Color customization", "Would you like to change the background color?")
    if bgChange:
        bgColor = askcolor(title="Background color picker")
        settings['DEFAULT']['bg'] = bgColor[1]
        PURPLE = bgColor[1]
    fgChange = messagebox.askyesno("Color customization", "Would you like to change the foreground color?")
    if fgChange:
        fgColor = askcolor(title="Foreground color picker")
        settings['DEFAULT']['fg'] = fgColor[1]
        BLACK = fgColor[1]
    for i in range(len(current_menu)):
        current_menu[i]['bg'] = PURPLE
        current_menu[i]['fg'] = BLACK
    window.config(background=PURPLE)
    f = open("settings.ini", "w")
    settings.write(f)
    f.close()


# next 9 definition display the specified commands gui
def displayMainMenu():
    global main_menu
    window.cog = PhotoImage("visualcontent\\cog.png")
    window.bind('<Return>', lambda event: submitCommand())
    main_menu.clear()
    title_label = Label(window, text="Aye Aye Capn!", font=("Orbitron", 25), fg=BLACK, bg=PURPLE)
    main_menu.append(title_label) #0
    rank_button = Button(window, cursor="hand2", text="Rank", font=("Orbitron", 20), bg=PURPLE, fg=BLACK, width=10, command=lambda: updateSelectedCommand(1))
    main_menu.append(rank_button) #1
    store_button = Button(window, cursor="hand2", text="Store", font=("Orbitron", 20), bg=PURPLE, fg=BLACK, width=10, command=lambda: updateSelectedCommand(2))
    main_menu.append(store_button) #2
    match_stats_button = Button(window, cursor="hand2", text="Match Stats", font=("Orbitron", 20), fg=BLACK, bg=PURPLE, width=10, command=lambda: updateSelectedCommand(3))
    main_menu.append(match_stats_button) #3
    match_skins_button = Button(window, cursor="hand2", text="Match Skins", font=("Orbitron", 20), fg=BLACK, bg=PURPLE, width=10, command=lambda: updateSelectedCommand(4))
    main_menu.append(match_skins_button) #4
    logout_button = Button(window, cursor="hand2", text="Logout", font=("Orbitron", 20), bg=PURPLE, fg=BLACK, width=10, command=lambda: updateSelectedCommand(5))
    main_menu.append(logout_button) #5
    submit_button = Button(window, cursor="hand2", text="Submit", font=("Orbitron", 20), bg=PURPLE, fg=BLACK, width=5, command=submitCommand)
    main_menu.append(submit_button) #6
    error_label = Label(window, text="", bg=PURPLE, fg="red", font=("Orbitron", 15))
    main_menu.append(error_label) #7
    help_button = Button(window, cursor="hand2", text="Help", font=("Orbitron", 20), bg=PURPLE, fg=BLACK, width=10, command=lambda: updateSelectedCommand(6))
    main_menu.append(help_button)  # 8
    created_by = Label(window, text="Created by Spherical-S on github", font=("Orbitron", 12), fg=BLACK, bg=PURPLE)
    main_menu.append(created_by) # 9
    logged_in_as = Label(window, text=f"Logged in as {decrypt(settings['DEFAULT']['username'], enc_key)}", font=("Orbitron", 12), fg=BLACK, bg=PURPLE)
    main_menu.append(logged_in_as) # 10
    settings_button = Button(window, cursor="hand2", text="⚙", font=("Orbitron", 12), bg=PURPLE, fg=BLACK, width=2, height=1, command=displaySettings)
    main_menu.append(settings_button) # 11
    title_label.place(x=311, y=5)
    rank_button.place(x=70, y=85)
    store_button.place(x=345, y=85)
    match_skins_button.place(x=70, y=250)
    match_stats_button.place(x=620, y=85)
    logout_button.place(x=345, y=250)
    help_button.place(x=620, y=250)
    submit_button.place(x=395, y=430)
    error_label.pack(pady=50)
    logged_in_as.pack(side=BOTTOM, anchor='se', pady=5)
    created_by.place(x=5, y=470)
    settings_button.place(x=5, y=5)


def displaySettings():
    resetArguments()
    destroyMainMenu()
    title_label = Label(window, text="Settings", font=("Orbitron", 25), fg=BLACK, bg=PURPLE)
    current_menu.append(title_label)  # 0
    back_button = Button(window, cursor="hand2", text="Back", font=("Orbitron", 15), bg=PURPLE, fg=BLACK, command=settingToMain)
    current_menu.append(back_button)  # 1
    color_button = Button(window, cursor="hand2", text="Customize colors", font=("Orbitron", 20), bg=PURPLE, fg=BLACK, width=14, command=customizeColors)
    current_menu.append(color_button)
    back_button.place(x=10, y=15)
    title_label.pack(pady=5)
    color_button.place(x=310, y=180)


def displayRankMenu(player, tag, region, act):
    window.unbind('<Return>')
    util.internet()
    loading_label = Label(window, text="Loading...", font=("Orbitron", 25), fg=BLACK, bg=PURPLE)
    loading_label.pack()
    loading_sublabel = Label(window, text="Please wait while the rank is being fetched", font=("Orbitron", 15), fg=BLACK, bg=PURPLE)
    loading_sublabel.pack()
    window.update()
    if act == "current":
        act = util.getCurrentSeason()
    xAct = int(act[1:2]) - 1
    output = util.getRankByName(player, tag, region, act, decrypt(settings['DEFAULT']['token'], enc_key), decrypt(settings['DEFAULT']['entitlement'], enc_key))
    if xAct < 4:
        image = Image.open(f"visualcontent\\ranksold\\{str(output[3])}.png")
    else:
        image = Image.open(f"visualcontent\\ranksnew\\{str(output[3])}.png")
    image = image.resize((200, 200))
    window.img = ImageTk.PhotoImage(image)
    title_label = Label(window, text="Rank", font=("Orbitron", 25), fg=BLACK, bg=PURPLE)
    current_menu.append(title_label) #0
    back_button = Button(window, cursor="hand2", text="Back", font=("Orbitron", 15), bg=PURPLE, fg=BLACK, command=submitCommand)
    current_menu.append(back_button) #1
    subtitle_label = Label(window, text=f"{player}#{tag} from {region}'s rank", font=("Orbitron", 15), fg=BLACK, bg=PURPLE)
    current_menu.append(subtitle_label)  #2
    rank_label = Label(window, text=f"Rank in {act}: {output[1]}, {output[2]} RR", font=("Orbitron", 18), fg=BLACK, bg=PURPLE)
    current_menu.append(rank_label)  #3
    max_rank_label = Label(window, text=f"Peak Rank: {output[4]}", font=("Orbitron", 18), fg=BLACK, bg=PURPLE)
    current_menu.append(max_rank_label)  #4
    max_act_label = Label(window, text=f"Peak Rank Act: {output[6]}", font=("Orbitron", 18), fg=BLACK, bg=PURPLE)
    current_menu.append(max_act_label)  #5
    note_label = Label(window, text=f"{output[7]}", font=("Orbitron", 18), fg=BLACK, bg=PURPLE)
    current_menu.append(note_label)  #6
    rank_image = Label(window, image=window.img, bg=PURPLE)
    current_menu.append(rank_image)
    loading_sublabel.destroy()
    loading_label.destroy()
    back_button.place(x=10, y=15)
    title_label.pack(pady=5)
    subtitle_label.pack()
    rank_label.place(x=20, y=170)
    max_rank_label.place(x=20, y=220)
    max_act_label.place(x=20, y=270)
    note_label.pack(side="bottom", pady=10)
    rank_image.place(x=660, y=135)


def displayStore():
    global current_skin
    window.unbind('<Return>')
    util.internet()
    loading_label = Label(window, text="Loading...", font=("Orbitron", 25), fg=BLACK, bg=PURPLE)
    loading_label.pack()
    loading_sublabel = Label(window, text="Please wait while your store is being fetched", font=("Orbitron", 15),fg=BLACK, bg=PURPLE)
    loading_sublabel.pack()
    window.update()
    t = decrypt(settings['DEFAULT']['token'], enc_key)
    en = decrypt(settings['DEFAULT']['entitlement'], enc_key)
    puuid = settings['DEFAULT']['puuid']
    region = settings['DEFAULT']['region']
    store = util.getStore(t, en, puuid, region)
    balance = util.getBalance(t, en, puuid, region)
    if store['status'] != 200:
        loading_sublabel.destroy()
        loading_label.destroy()
        title_label = Label(window, text="Store", font=("Orbitron", 25), fg=BLACK, bg=PURPLE)
        current_menu.append(title_label)  # 0
        back_button = Button(window, cursor="hand2", text="Back", font=("Orbitron", 15), bg=PURPLE, fg=BLACK, command=submitCommand)
        current_menu.append(back_button)  # 1
        error_label = Label(window, text="Something went wrong, please try re logging in then try again!", font=("Orbitron", 15), fg=BLACK, bg=PURPLE)
        current_menu.append(error_label)
        loading_sublabel.destroy()
        loading_label.destroy()
        back_button.place(x=10, y=15)
        title_label.pack(pady=5)
        error_label.pack()
        return
    window.temp = []
    current_skin = 0
    for i in range(len(store['uuids'])):
        window.temp.append(util.photoImagify(f"https://media.valorant-api.com/weaponskinlevels/{store['uuids'][i]}/displayicon.png"))
    title_label = Label(window, text="Store", font=("Orbitron", 25), fg=BLACK, bg=PURPLE)
    current_menu.append(title_label)  #0
    back_button = Button(window, cursor="hand2", text="Back", font=("Orbitron", 15), bg=PURPLE, fg=BLACK, command=submitCommand)
    current_menu.append(back_button)  #1
    next_button = Button(window, cursor="hand2", text="-->", font=("Orbitron", 25), bg=PURPLE, command=lambda store=store: nextSkin(store))
    current_menu.append(next_button) #2
    prev_button = Button(window, cursor="hand2", text="<--", font=("Orbitron", 25), bg=PURPLE, command=lambda store=store: prevSkin(store))
    current_menu.append(prev_button) #3
    image = Image.open(f"visualcontent\\vp.png")
    image = image.resize((40, 40))
    window.vpimg = ImageTk.PhotoImage(image)
    vp_label = Label(window, text=f": {balance[0]}", font=("Orbitron", 15), bg=PURPLE, fg=BLACK, image=window.vpimg, compound="left")
    current_menu.append(vp_label) #4
    image = Image.open(f"visualcontent\\rp.png")
    image = image.resize((40, 40))
    window.rpimg = ImageTk.PhotoImage(image)
    rp_label = Label(window, text=f": {balance[1]}", font=("Orbitron", 15), bg=PURPLE, fg=BLACK, image=window.rpimg, compound="left")
    current_menu.append(rp_label) #5
    skin_label = Label(window, text=f"{store['displayNames'][0][0][:40]}", font=("Orbitron", 20), fg=BLACK, bg=PURPLE, image=window.temp[0], compound="top")
    current_menu.append(skin_label) #6
    cost_label = Label(window, text=f": {store['displayNames'][0][1]}", font=("Orbitron", 15), bg=PURPLE, fg=BLACK, image=window.vpimg, compound="left")
    current_menu.append(cost_label)
    loading_sublabel.destroy()
    loading_label.destroy()
    back_button.place(x=10, y=15)
    title_label.pack(pady=5)
    next_button.place(x=795, y=210)
    prev_button.place(x=20, y=210)
    skin_label.pack(pady=(90, 10))
    cost_label.pack()
    vp_label.place(x=300, y=440)
    rp_label.place(x=500, y=440)


def displayMatchStats():
    global displayData
    window.unbind('<Return>')
    util.internet()
    loading_label = Label(window, text="Loading...", font=("Orbitron", 25), fg=BLACK, bg=PURPLE)
    loading_label.pack()
    loading_sublabel = Label(window, text="Please wait while your match stats are being fetched", font=("Orbitron", 15), fg=BLACK, bg=PURPLE)
    loading_sublabel.pack()
    window.update()
    t = decrypt(settings['DEFAULT']['token'], enc_key)
    en = decrypt(settings['DEFAULT']['entitlement'], enc_key)
    puuid = settings['DEFAULT']['puuid']
    region = settings['DEFAULT']['region']
    output = util.matchStats(t, en, puuid, region)
    if output['status'] == -1:
        loading_sublabel.destroy()
        loading_label.destroy()
        title_label = Label(window, text="Match Stats", font=("Orbitron", 25), fg=BLACK, bg=PURPLE)
        current_menu.append(title_label)  #0
        back_button = Button(window, cursor="hand2", text="Back", font=("Orbitron", 15), bg=PURPLE, fg=BLACK, command=submitCommand)
        current_menu.append(back_button)  #1
        error_label = Label(window, text="You must currently be in a game to use this command", font=("Orbitron", 15), fg=BLACK, bg=PURPLE)
        current_menu.append(error_label)
        loading_sublabel.destroy()
        loading_label.destroy()
        back_button.place(x=10, y=15)
        title_label.pack(pady=5)
        error_label.pack()
    else:
        if output["type"] == "pre":
            loading_sublabel.destroy()
            loading_label.destroy()
            displayData = {}
            displayData['currentTeam'] = "Ally"
            displayData['AllyNames'] = "Player\n            \n"
            displayData['AllyRanks'] = "Rank\n          \n"
            displayData['AllyRRs'] = "RR\n   \n"
            displayData['AllyPeaks'] = "Peak\n          \n"
            displayData['AllyPeakSeasons'] = "Peak\nAct\n"
            for i in range(len(output['allies'])):
                displayData['AllyNames'] += f"{output['allies'][i]['name'][:12]}\n({output['allies'][i]['agent']})\n"
                displayData['AllyRanks'] += output['allies'][i]['rank'] + "\n\n"
                displayData['AllyRRs'] += output['allies'][i]['rr'] + "\n\n"
                displayData['AllyPeaks'] += output['allies'][i]['peak'] + "\n\n"
                displayData['AllyPeakSeasons'] += output['allies'][i]['peakSeason'] + "\n\n"
            title_label = Label(window, text="Match Stats", font=("Orbitron", 25), fg=BLACK, bg=PURPLE)
            current_menu.append(title_label)  # 0
            back_button = Button(window, cursor="hand2", text="Back", font=("Orbitron", 15), bg=PURPLE, fg=BLACK, command=submitCommand)
            current_menu.append(back_button)  # 1
            team_label = Label(window, text=displayData['currentTeam'] + " Team", font=("Orbitron", 20), fg=BLACK, bg=PURPLE)
            current_menu.append(team_label)  # 2
            names_label = Label(window, text=displayData['AllyNames'], font=("Orbitron", 15), fg=BLACK, bg=PURPLE)
            current_menu.append(names_label)  # 3
            ranks_label = Label(window, text=displayData['AllyRanks'], font=("Orbitron", 15), fg=BLACK, bg=PURPLE)
            current_menu.append(ranks_label)  # 4
            rrs_label = Label(window, text=displayData['AllyRRs'], font=("Orbitron", 15), fg=BLACK, bg=PURPLE)
            current_menu.append(rrs_label)  # 5
            peaks_label = Label(window, text=displayData['AllyPeaks'], font=("Orbitron", 15), fg=BLACK, bg=PURPLE)
            current_menu.append(peaks_label)  # 6
            peakSeasons_label = Label(window, text=displayData['AllyPeakSeasons'], font=("Orbitron", 15), fg=BLACK, bg=PURPLE)
            current_menu.append(peakSeasons_label)  # 7
            back_button.place(x=10, y=15)
            title_label.pack(pady=5)
            team_label.pack()
            names_label.place(x=110, y=120)
            ranks_label.place(x=310, y=120)
            rrs_label.place(x=470, y=120)
            peaks_label.place(x=530, y=120)
            peakSeasons_label.place(x=710, y=120)
            return
        if output['ffa'] == 0:
            loading_sublabel.destroy()
            loading_label.destroy()
            displayData = {}
            displayData['currentTeam'] = "Blue"
            displayData['blueNames'] = "Player\n            \n"
            displayData['blueRanks'] = "Rank\n          \n"
            displayData['blueRRs'] = "RR\n   \n"
            displayData['bluePeaks'] = "Peak\n          \n"
            displayData['bluePeakSeasons'] = "Peak\nAct\n"
            for i in range(len(output['blueTeam'])):
                displayData['blueNames'] += f"{output['blueTeam'][i]['name'][:12]}\n({output['blueTeam'][i]['agent']})\n"
                displayData['blueRanks'] += output['blueTeam'][i]['rank'] + "\n\n"
                displayData['blueRRs'] += output['blueTeam'][i]['rr'] + "\n\n"
                displayData['bluePeaks'] += output['blueTeam'][i]['peak'] + "\n\n"
                displayData['bluePeakSeasons'] += output['blueTeam'][i]['peakSeason'] + "\n\n"
            displayData['redNames'] = "Player\n\n"
            displayData['redRanks'] = "Rank\n\n"
            displayData['redRRs'] = "RR\n\n"
            displayData['redPeaks'] = "Peak\n\n"
            displayData['redPeakSeasons'] = "Act Of\nPeak\n"
            for i in range(len(output['redTeam'])):
                displayData['redNames'] += f"{output['redTeam'][i]['name'][:12]}\n({output['redTeam'][i]['agent']})\n"
                displayData['redRanks'] += output['redTeam'][i]['rank'] + "\n\n"
                displayData['redRRs'] += output['redTeam'][i]['rr'] + "\n\n"
                displayData['redPeaks'] += output['redTeam'][i]['peak'] + "\n\n"
                displayData['redPeakSeasons'] += output['redTeam'][i]['peakSeason'] + "\n\n"
            title_label = Label(window, text="Match Stats", font=("Orbitron", 25), fg=BLACK, bg=PURPLE)
            current_menu.append(title_label)  # 0
            back_button = Button(window, cursor="hand2", text="Back", font=("Orbitron", 15), bg=PURPLE, fg=BLACK, command=submitCommand)
            current_menu.append(back_button)  # 1
            next_button = Button(window, cursor="hand2", text="-->", font=("Orbitron", 25), bg=PURPLE, command=nextTeam)
            current_menu.append(next_button)  # 2
            prev_button = Button(window, cursor="hand2", text="<--", font=("Orbitron", 25), bg=PURPLE, command=nextTeam)
            current_menu.append(prev_button)  # 3
            team_label = Label(window, text=displayData['currentTeam']+" Team", font=("Orbitron", 20), fg=BLACK, bg=PURPLE)
            current_menu.append(team_label) # 4
            names_label = Label(window, text=displayData['blueNames'], font=("Orbitron", 15), fg=BLACK, bg=PURPLE)
            current_menu.append(names_label) # 5
            ranks_label = Label(window, text=displayData['blueRanks'], font=("Orbitron", 15), fg=BLACK, bg=PURPLE)
            current_menu.append(ranks_label)  # 6
            rrs_label = Label(window, text=displayData['blueRRs'], font=("Orbitron", 15), fg=BLACK, bg=PURPLE)
            current_menu.append(rrs_label)  # 7
            peaks_label = Label(window, text=displayData['bluePeaks'], font=("Orbitron", 15), fg=BLACK, bg=PURPLE)
            current_menu.append(peaks_label)  # 8
            peakSeasons_label = Label(window, text=displayData['bluePeakSeasons'], font=("Orbitron", 15), fg=BLACK, bg=PURPLE)
            current_menu.append(peakSeasons_label)  # 9
            back_button.place(x=10, y=15)
            title_label.pack(pady=5)
            team_label.pack()
            next_button.place(x=795, y=210)
            prev_button.place(x=20, y=210)
            names_label.place(x=110, y=120)
            ranks_label.place(x=310, y=120)
            rrs_label.place(x=470, y=120)
            peaks_label.place(x=530, y=120)
            peakSeasons_label.place(x=710, y=120)
        else:
            loading_sublabel.destroy()
            loading_label.destroy()
            displayData = {}
            displayData['currentTeam'] = "FFA"
            displayData['names'] = "Player\n            \n"
            displayData['ranks'] = "Rank\n          \n"
            displayData['RRs'] = "RR\n   \n"
            displayData['peaks'] = "Peak\n          \n"
            displayData['peakSeasons'] = "Peak\nAct\n"
            for i in range(len(output['players'])):
                displayData['names'] += f"{output['players'][i]['name'][:12]}\n({output['players'][i]['agent']})\n"
                displayData['ranks'] += output['players'][i]['rank'] + "\n\n"
                displayData['RRs'] += output['players'][i]['rr'] + "\n\n"
                displayData['peaks'] += output['players'][i]['peak'] + "\n\n"
                displayData['peakSeasons'] += output['players'][i]['peakSeason'] + "\n\n"
            top_frame = Frame(window, width=900, height=125, bg=PURPLE)
            top_frame.grid(row=0, column=0, pady=5, sticky='n')
            top_frame.grid_propagate(False)
            bottom_frame = Frame(window, width=900, height=365, bg=PURPLE)
            bottom_frame.grid(row=1, column=0, pady=5, sticky='s')
            current_menu.append(top_frame)
            current_menu.append(bottom_frame)
            title_label = Label(top_frame, text="Match Stats", font=("Orbitron", 25), fg=BLACK, bg=PURPLE)
            title_label.grid(row=0, column=1, padx=250)
            back_button = Button(top_frame, cursor="hand2", text="Back", font=("Orbitron", 15), bg=PURPLE, fg=BLACK, command=submitCommand)
            back_button.grid(row=0, column=0, padx=5)
            team_label = Label(top_frame, text="FFA", font=("Orbitron", 20), fg=BLACK, bg=PURPLE)
            team_label.grid(row=1, column=1, pady=5)
            canvas = Canvas(bottom_frame, height=365, width=885, bg=PURPLE, highlightthickness=0)
            canvas.grid(row=0, column=0)
            scroll = Scrollbar(bottom_frame, orient=VERTICAL, command=canvas.yview)
            scroll.grid(row=0, column=1, sticky='ns')
            canvas.configure(yscrollcommand=scroll.set)
            canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
            display_frame = Frame(canvas, bg=PURPLE)
            canvas.create_window((0, 0), window=display_frame, anchor='n')
            names_label = Label(display_frame, text=displayData['names'], font=("Orbitron", 15), fg=BLACK, bg=PURPLE)
            names_label.grid(row=0, column=0, padx=25)
            ranks_label = Label(display_frame, text=displayData['ranks'], font=("Orbitron", 15), fg=BLACK, bg=PURPLE)
            ranks_label.grid(row=0, column=1, padx=25)
            rrs_label = Label(display_frame, text=displayData['RRs'], font=("Orbitron", 15), fg=BLACK, bg=PURPLE)
            rrs_label.grid(row=0, column=2, padx=25)
            peaks_label = Label(display_frame, text=displayData['peaks'], font=("Orbitron", 15), fg=BLACK, bg=PURPLE)
            peaks_label.grid(row=0, column=3, padx=25)
            peakSeasons_label = Label(display_frame, text=displayData['peakSeasons'], font=("Orbitron", 15), fg=BLACK, bg=PURPLE)
            peakSeasons_label.grid(row=0, column=4, padx=25)


def displayMatchSkins():
    global displayData
    global mSkinsOutput
    window.unbind('<Return>')
    util.internet()
    loading_label = Label(window, text="Loading...", font=("Orbitron", 25), fg=BLACK, bg=PURPLE)
    loading_label.pack()
    loading_sublabel = Label(window, text="Please wait while your match stats are being fetched", font=("Orbitron", 15),fg=BLACK, bg=PURPLE)
    loading_sublabel.pack()
    window.update()
    t = decrypt(settings['DEFAULT']['token'], enc_key)
    en = decrypt(settings['DEFAULT']['entitlement'], enc_key)
    puuid = settings['DEFAULT']['puuid']
    region = settings['DEFAULT']['region']
    output = util.matchSkins(t, en, puuid, region)
    mSkinsOutput = output
    if output['status'] == -1:
        loading_sublabel.destroy()
        loading_label.destroy()
        title_label = Label(window, text="Match Skins", font=("Orbitron", 25), fg=BLACK, bg=PURPLE)
        current_menu.append(title_label)  # 0
        back_button = Button(window, cursor="hand2", text="Back", font=("Orbitron", 15), bg=PURPLE, fg=BLACK, command=submitCommand)
        current_menu.append(back_button)  # 1
        error_label = Label(window, text="You must currently be in a game to use this command", font=("Orbitron", 15), fg=BLACK, bg=PURPLE)
        current_menu.append(error_label)
        loading_sublabel.destroy()
        loading_label.destroy()
        back_button.place(x=10, y=15)
        title_label.pack(pady=5)
        error_label.pack()
    if output['status'] == -2:
        loading_sublabel.destroy()
        loading_label.destroy()
        title_label = Label(window, text="Match Skins", font=("Orbitron", 25), fg=BLACK, bg=PURPLE)
        current_menu.append(title_label)  # 0
        back_button = Button(window, cursor="hand2", text="Back", font=("Orbitron", 15), bg=PURPLE, fg=BLACK, command=submitCommand)
        current_menu.append(back_button)  # 1
        error_label = Label(window, text="Due to a bug within riot games system,\nmatch skins only works after agent select.", font=("Orbitron", 15), fg=BLACK, bg=PURPLE)
        current_menu.append(error_label)
        loading_sublabel.destroy()
        loading_label.destroy()
        back_button.place(x=10, y=15)
        title_label.pack(pady=5)
        error_label.pack()
    if output['status'] == 200:
        if output['ffa'] == 0:
            loading_sublabel.destroy()
            loading_label.destroy()
            displayData = {}
            displayData['currentTeam'] = "Blue"
            displayData['currentGun'] = "Vandal"
            displayData['blueNames'] = "Player\n============\n"
            displayData['blueSkins'] = "Skin\n==============================\n"
            for i in range(len(output['blueTeam'])):
                displayData['blueNames'] += f"{output['blueTeam'][i]['name'][:12]}\n({output['blueTeam'][i]['agent']})\n"
                displayData['blueSkins'] += output['blueTeam'][i]['skins']['Vandal'][:30] + "\n\n"
            displayData['redNames'] = "Player\n============\n"
            displayData['redSkins'] = "Skin\n==============================\n"
            for i in range(len(output['redTeam'])):
                displayData['redNames'] += f"{output['redTeam'][i]['name'][:12]}\n({output['redTeam'][i]['agent']})\n"
                displayData['redSkins'] += output['redTeam'][i]['skins']['Vandal'][:30] + "\n\n"
            title_label = Label(window, text="Match Stats", font=("Orbitron", 25), fg=BLACK, bg=PURPLE)
            current_menu.append(title_label)  # 0
            back_button = Button(window, cursor="hand2", text="Back", font=("Orbitron", 15), bg=PURPLE, fg=BLACK, command=submitCommand)
            current_menu.append(back_button)  # 1
            next_button = Button(window, cursor="hand2", text="-->", font=("Orbitron", 25), bg=PURPLE, command=nextTeamSkins)
            current_menu.append(next_button)  # 2
            prev_button = Button(window, cursor="hand2", text="<--", font=("Orbitron", 25), bg=PURPLE, command=nextTeamSkins)
            current_menu.append(prev_button)  # 3
            team_label = Label(window, text=displayData['currentTeam'] + " Team", font=("Orbitron", 20), fg=BLACK, bg=PURPLE)
            current_menu.append(team_label)  # 4
            names_label = Label(window, text=displayData['blueNames'], font=("Orbitron", 15), fg=BLACK, bg=PURPLE)
            current_menu.append(names_label)  # 5
            var = StringVar(window)
            temp = ['Vandal', 'Phantom', 'Operator', 'Sheriff', 'Ghost',
                    'Classic', 'Spectre', 'Bulldog', 'Odin', 'Ares', 'Guardian',
                    'Marshal', 'Stinger', 'Bucky', 'Judge', 'Frenzy', 'Shorty', 'Melee']
            var.set(temp[0])
            gun_width = len(max(temp, key=len))
            args_list.append(var)
            gun_select = OptionMenu(window, var, *temp, command=changeGun)
            gun_select.config(bg=PURPLE, font=("Orbitron", 12), highlightthickness=0, width=gun_width)
            current_menu.append(gun_select)  # 6
            skins_label = Label(window, text=displayData['blueSkins'], font=("Orbitron", 15), fg=BLACK, bg=PURPLE)
            current_menu.append(skins_label)  # 7
            back_button.place(x=10, y=15)
            title_label.pack(pady=5)
            team_label.pack()
            next_button.place(x=795, y=210)
            prev_button.place(x=20, y=210)
            names_label.place(x=150, y=120)
            skins_label.place(x=350, y=120)
            gun_select.place(x=750, y=15)
        else:
            loading_sublabel.destroy()
            loading_label.destroy()
            displayData = {}
            displayData['currentTeam'] = "FFA"
            displayData['currentGun'] = "Vandal"
            displayData['playerNames'] = "Player\n============\n"
            displayData['playerSkins'] = "Skin\n==============================\n"
            for i in range(len(output['players'])):
                displayData['playerNames'] += f"{output['players'][i]['name'][:12]}\n({output['players'][i]['agent']})\n"
                displayData['playerSkins'] += output['players'][i]['skins']['Vandal'][:30] + "\n\n"
            top_frame = Frame(window, width=900, height=125, bg=PURPLE)
            top_frame.grid(row=0, column=0, pady=5, sticky='n')
            top_frame.grid_propagate(False)
            bottom_frame = Frame(window, width=900, height=365, bg=PURPLE)
            bottom_frame.grid(row=1, column=0, pady=5, sticky='s')
            current_menu.append(top_frame) #0
            current_menu.append(bottom_frame) #1
            title_label = Label(top_frame, text="Match Skins", font=("Orbitron", 25), fg=BLACK, bg=PURPLE)
            title_label.grid(row=0, column=1, padx=(250, 170))
            back_button = Button(top_frame, cursor="hand2", text="Back", font=("Orbitron", 15), bg=PURPLE, fg=BLACK, command=submitCommand)
            back_button.grid(row=0, column=0, padx=5)
            team_label = Label(top_frame, text="FFA", font=("Orbitron", 20), fg=BLACK, bg=PURPLE)
            team_label.grid(row=1, column=1, pady=5, padx=(90, 0))
            var = StringVar(window)
            temp = ['Vandal', 'Phantom', 'Operator', 'Sheriff', 'Ghost',
                    'Classic', 'Spectre', 'Bulldog', 'Odin', 'Ares', 'Guardian',
                    'Marshal', 'Stinger', 'Bucky', 'Judge', 'Frenzy', 'Shorty', 'Melee']
            var.set(temp[0])
            gun_width = len(max(temp, key=len))
            args_list.append(var)
            gun_select = OptionMenu(top_frame, var, *temp, command=changeGun)
            gun_select.config(bg=PURPLE, font=("Orbitron", 12), highlightthickness=0, width=gun_width)
            gun_select.grid(row=0, column=2)
            canvas = Canvas(bottom_frame, height=365, width=885, bg=PURPLE, highlightthickness=0)
            canvas.grid(row=0, column=0)
            scroll = Scrollbar(bottom_frame, orient=VERTICAL, command=canvas.yview)
            scroll.grid(row=0, column=1, sticky='ns')
            canvas.configure(yscrollcommand=scroll.set)
            canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
            display_frame = Frame(canvas, bg=PURPLE)
            canvas.create_window((0, 0), window=display_frame, anchor='n')
            names_label = Label(display_frame, text=displayData['playerNames'], font=("Orbitron", 15), fg=BLACK, bg=PURPLE)
            names_label.grid(row=0, column=0, padx=100)
            skins_label = Label(display_frame, text=displayData['playerSkins'], font=("Orbitron", 15), fg=BLACK, bg=PURPLE)
            skins_label.grid(row=0, column=1, padx=10)
            current_menu.append(skins_label) #2


def displayLogout():
    global region_buttons
    global logins_check
    window.unbind('<Return>')
    settings['DEFAULT']['username'] = ""
    settings['DEFAULT']['password'] = ""
    settings['DEFAULT']['region'] = ""
    settings['DEFAULT']['token'] = ""
    settings['DEFAULT']['entitlement'] = ""
    settings['DEFAULT']['puuid'] = ""
    settings['DEFAULT']['mfa'] = ""
    settings['DEFAULT']['expiry'] = ""
    f = open("settings.ini", "w")
    settings.write(f)
    f.close()
    window.bind("<Return>", login)
    region_buttons = [0, 0, 0, 0]
    displayLogin()
    region_buttons[0] = Button(window, cursor="hand2", text="NA", font=("Orbitron", 20), fg=BLACK, bg=PURPLE, command=lambda num=0: selectRegion(num))
    region_buttons[1] = Button(window, cursor="hand2", text="EU", font=("Orbitron", 20), fg=BLACK, bg=PURPLE, command=lambda num=1: selectRegion(num))
    region_buttons[2] = Button(window, cursor="hand2", text="AP", font=("Orbitron", 20), fg=BLACK, bg=PURPLE, command=lambda num=2: selectRegion(num))
    region_buttons[3] = Button(window, cursor="hand2", text="KR", font=("Orbitron", 20), fg=BLACK, bg=PURPLE, command=lambda num=3: selectRegion(num))
    region_buttons[0].place(x=170, y=300)
    region_buttons[1].place(x=320, y=300)
    region_buttons[2].place(x=470, y=300)
    region_buttons[3].place(x=620, y=300)


def displayHelp():
    window.unbind('<Return>')
    title_label = Label(window, text="Help", font=("Orbitron", 25), fg=BLACK, bg=PURPLE)
    current_menu.append(title_label)  #0
    back_button = Button(window, cursor="hand2", text="Back", font=("Orbitron", 15), bg=PURPLE, fg=BLACK, command=submitCommand)
    current_menu.append(back_button)  # 1
    bug_label = Label(window, text="Found a bug? Contact the dev with one of the following:\nDiscord: tiddybite#6304\nEmail: sadiq.shahid101@gmail.com\n ", font=("Orbitron", 15), fg=BLACK, bg=PURPLE)
    current_menu.append(bug_label) #2
    donate_label = Label(window, text="\nDonations are not needed but always appreciated!\nClick here to donate", font=("Orbitron", 15), fg=BLACK, bg=PURPLE, cursor="hand2")
    current_menu.append(donate_label)  # 3
    donate_label.bind("<Button-1>", lambda e: hyperlink('https://ko-fi.com/spherical'))
    back_button.place(x=10, y=15)
    title_label.pack(pady=5)
    bug_label.pack()
    donate_label.pack(pady=5)


def displayLogin():
    window.bind("<Return>", login)
    title_label = Label(window, text="Please log in:", font=("Orbitron", 25), fg=BLACK, bg=PURPLE)
    current_menu.append(title_label) #0
    username_label = Label(window, text="Username:", font=("Orbitron", 15), fg=BLACK, bg=PURPLE)
    current_menu.append(username_label) #1
    username_input = Entry(window, font=("Orbitron", 25), fg=BLACK, bg=PURPLE, width=15)
    current_menu.append(username_input) #2
    password_label = Label(window, text="Password:", font=("Orbitron", 15), fg=BLACK, bg=PURPLE)
    current_menu.append(password_label) #3
    password_input = Entry(window, font=("Orbitron", 25), fg=BLACK, bg=PURPLE, width=15, show="*")
    current_menu.append(password_input) #4
    enter_button = Button(window, cursor="hand2", text="Enter", command=lambda self=window: login(self), font=("Orbitron", 20), bg=PURPLE)
    current_menu.append(enter_button) #5
    region_label = Label(window, text="Select a region:", font=("Orbitron", 15), fg=BLACK, bg=PURPLE)
    current_menu.append(region_label) #6
    error_label = Label(window, text="", bg=PURPLE, fg="red", font=("Orbitron", 15))
    current_menu.append(error_label) #7
    title_label.pack()
    username_label.place(x=10, y=75)
    username_input.place(x=10, y=100)
    password_label.place(x=450, y=75)
    password_input.place(x=450, y=100)
    enter_button.pack(side="bottom", pady=5)
    region_label.place(x=350, y=200)
    error_label.pack(side="bottom", pady=10)


# next 2 definitions switch the display for which skin in the users shop is being displayed
def nextSkin(store):
    global current_menu
    global current_skin
    if current_skin == 3:
        current_skin = 0
    else:
        current_skin += 1
    current_menu[6]['text'] = f"{store['displayNames'][current_skin][0][:40]}"
    current_menu[6]['image'] = f"{window.temp[current_skin]}"
    current_menu[7]['text'] = f"{store['displayNames'][current_skin][1]}"


def prevSkin(store):
    global current_menu
    global current_skin
    if current_skin == 0:
        current_skin = 3
    else:
        current_skin -= 1
    current_menu[6]['text'] = f"{store['displayNames'][current_skin][0][:40]}"
    current_menu[6]['image'] = f"{window.temp[current_skin]}"
    current_menu[7]['text'] = f"{store['displayNames'][current_skin][1]}"

# switches the display between teams for matchStats
def nextTeam():
    global displayData
    if displayData['currentTeam'] == "Blue":
        displayData['currentTeam'] = "Red"
        current_menu[4]['text'] = "Red"
        current_menu[5]['text'] = displayData['redNames']
        current_menu[6]['text'] = displayData['redRanks']
        current_menu[7]['text'] = displayData['redRRs']
        current_menu[8]['text'] = displayData['redPeaks']
        current_menu[9]['text'] = displayData['redPeakSeasons']
    else:
        displayData['currentTeam'] = "Blue"
        current_menu[4]['text'] = "Blue"
        current_menu[5]['text'] = displayData['blueNames']
        current_menu[6]['text'] = displayData['blueRanks']
        current_menu[7]['text'] = displayData['blueRRs']
        current_menu[8]['text'] = displayData['bluePeaks']
        current_menu[9]['text'] = displayData['bluePeakSeasons']


# switches the display between teams for matchSkins
def nextTeamSkins():
    global displayData
    if displayData['currentTeam'] == "Blue":
        displayData['currentTeam'] = "Red"
        current_menu[4]['text'] = "Red"
        current_menu[5]['text'] = displayData['redNames']
        current_menu[7]['text'] = displayData['redSkins']
    else:
        displayData['currentTeam'] = "Blue"
        current_menu[4]['text'] = "Blue"
        current_menu[5]['text'] = displayData['blueNames']
        current_menu[7]['text'] = displayData['blueSkins']


# switches which gun's skins are being displayed for matchSkins
def changeGun(newGun):
    global displayData
    global mSkinsOutput
    displayData['currentGun'] = newGun
    if mSkinsOutput['ffa'] == 0:
        displayData['blueSkins'] = "Skin\n==============================\n"
        for i in range(len(mSkinsOutput['blueTeam'])):
            displayData['blueSkins'] += mSkinsOutput['blueTeam'][i]['skins'][newGun][:30] + "\n\n"
        displayData['redSkins'] = "Skin\n==============================\n"
        for i in range(len(mSkinsOutput['redTeam'])):
            displayData['redSkins'] += mSkinsOutput['redTeam'][i]['skins'][newGun][:30] + "\n\n"
        if displayData['currentTeam'] == "Blue":
            current_menu[7]['text'] = displayData['blueSkins']
        else:
            current_menu[7]['text'] = displayData['redSkins']
    else:
        displayData['playerSkins'] = "Skin\n==============================\n"
        for i in range(len(mSkinsOutput['players'])):
            displayData['playerSkins'] += mSkinsOutput['players'][i]['skins'][newGun][:30] + "\n\n"
        current_menu[2]['text'] = displayData['playerSkins']


# updates the colour of the region buttons depending on which one is selected
def selectRegion(regionNum):
    global region
    global region_buttons
    for i in range(4):
        if i == regionNum:
            region_buttons[i]['bg'] = "green"
            if i == 0:
                region = "na"
            elif i == 1:
                region = "eu"
            elif i == 2:
                region = "ap"
            elif i == 3:
                region = "kr"
        else:
            region_buttons[i]['bg'] = PURPLE


# sends api call to log in, then writes it into settings.ini
def login(self):
    global region
    logging.info('made it into login()')
    current_menu[7]['text'] = "Checking logins, please wait!"
    window.update()
    username = current_menu[2].get()
    password = current_menu[4].get()
    if username == "" or password == "" or region == "":
        current_menu[7]['text'] = "Missing fields!"
    else:
        authorization = getAuth(username, password)
        settings.read('settings.ini')
        if authorization[0] == "-1":
            current_menu[7]['text'] = "Invalid logins!"
        else:
            settings['DEFAULT']['username'] = encrypt(username, enc_key)
            settings['DEFAULT']['password'] = encrypt(password, enc_key)
            settings['DEFAULT']['region'] = region
            settings['DEFAULT']['expiry'] = "0"
            if settings['DEFAULT']['mfa'] == "1":
                now = datetime.now()
                exp = int(now.strftime("%Y%m%d%H%M%S"))
                exp += 10000
                settings['DEFAULT']['expiry'] = str(exp)
            f = open("settings.ini", "w")
            settings.write(f)
            f.close()
            for i in current_menu:
                i.destroy()
            for i in region_buttons:
                i.destroy()
            region_buttons.clear()
            current_menu.clear()
            settings.read('settings.ini')
            displayMainMenu()


try: # Put it all in a try... except to catch all errors and log them
    ### INITIALIZING IMPORTANT VARIABLES ###
    settings = ConfigParser()
    settings.read('settings.ini')
    PURPLE = settings['DEFAULT']['bg']
    BLACK = settings['DEFAULT']['fg']
    current_version = "1.1.1"
    region = ""
    enc_key = "0"
    selected_command = 0
    args_list = []
    util.internet()
    actsDictionary = util.getActs()
    agentsDictionary = util.getAgents()
    main_menu = []
    current_menu = []
    current_skin = 0
    displayData = {}
    mSkinsOutput = {}
    region_buttons = [0, 0, 0, 0]
    log_dir = ""
    logging.basicConfig(filename=(log_dir + "logs.txt"), level=logging.DEBUG, format='%(message)s')
    f = open('logs.txt', 'w')
    f.truncate(0)
    f.close()

    #### CREATING STARTUP UI ####
    # Checking to see if the Orbitron font exists on the machine
    window = Tk()
    if not ('Orbitron' in TkFont.families()):
        font.add_file('Orbitron-Bold.ttf')
    window.geometry("900x500")
    window.title("Capn")
    icon = PhotoImage(file="icon.ico")
    window.iconphoto(True, icon)
    window.config(background=PURPLE)
    window.resizable(False, False)
    check_logins_label = Label(window, text="Checking logins... Please wait\n(may take up to 15 seconds)", font=('Orbitron', 25), fg=BLACK, bg=PURPLE)
    check_logins_label.pack()
    window.update()
    util.internet()

    #Checking if the key for encrypting is set
    if len(settings['DEFAULT']['CAPNKEY']) != 8:
        enc_key = util.randomString(8)
        settings['DEFAULT']['CAPNKEY'] = enc_key
        f = open('settings.ini', 'w')
        settings.write(f)
        f.close()
    else:
        enc_key = settings['DEFAULT']['CAPNKEY']

    #### CHECKING FOR UPDATE ####
    r = get(url='https://raw.githubusercontent.com/Spherical-S/Capn-Valorant-Statistics-App/main/Verion.txt')
    version = str(r.content)[2:7]
    if version != current_version:
        update = messagebox.askyesno("Update available!", "There is an update for Capn - Valorant Statistics App. Go to download page?")
        if update:
            hyperlink('https://github.com/Spherical-S/Capn-Valorant-Statistics-App/releases')

    logins_check = checkLogins()
    ### CHECK LOGINS AND GET TOKEN, ENTITLEMENT AND PUUID ###
    if logins_check[0] == 0:
        check_logins_label.destroy()
        settings.read('settings.ini')
        displayMainMenu()
    elif logins_check[0] == 1:
        check_logins_label.destroy()
        settings['DEFAULT']['username'] = ""
        settings['DEFAULT']['password'] = ""
        settings['DEFAULT']['region'] = ""
        settings['DEFAULT']['token'] = ""
        settings['DEFAULT']['entitlement'] = ""
        settings['DEFAULT']['puuid'] = ""
        settings['DEFAULT']['mfa'] = ""
        settings['DEFAULT']['expiry'] = ""
        f = open("settings.ini", "w")
        settings.write(f)
        f.close()
        window.bind("<Return>", login)
        displayLogin()
        region_buttons[0] = Button(window, cursor="hand2", text="NA", font=("Orbitron", 20), fg=BLACK, bg=PURPLE, command=lambda num=0: selectRegion(num))
        region_buttons[1] = Button(window, cursor="hand2", text="EU", font=("Orbitron", 20), fg=BLACK, bg=PURPLE, command=lambda num=1: selectRegion(num))
        region_buttons[2] = Button(window, cursor="hand2", text="AP", font=("Orbitron", 20), fg=BLACK, bg=PURPLE, command=lambda num=2: selectRegion(num))
        region_buttons[3] = Button(window, cursor="hand2", text="KR", font=("Orbitron", 20), fg=BLACK, bg=PURPLE, command=lambda num=3: selectRegion(num))
        region_buttons[0].place(x=170, y=300)
        region_buttons[1].place(x=320, y=300)
        region_buttons[2].place(x=470, y=300)
        region_buttons[3].place(x=620, y=300)

    mainloop()
except Exception as e:
    logging.exception("Fatal error!")
    print_exc()