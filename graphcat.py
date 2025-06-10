#!/usr/bin/env python3

import argparse
from collections import Counter
import calendar
import time
import os
import re
import string
import sys
from typing import Dict, List
import tempfile
import shutil
import difflib

from jinja2 import Environment, FileSystemLoader
import matplotlib.pyplot as plt

TRANSLATIONS = {
    'en': {
        'lang_code': 'en',
        'page_title': 'Password Cracking Report',
        'title': 'Password Cracking Report',
        'total_hashes': 'Total hashes submitted:',
        'passwords_found': 'Passwords found:',
        'passwords_not_found': 'Passwords not found:',
        'percent_recovered': 'Percent of recovered passwords:',
        'section_format': 'Password Format repartition',
        'section_length': 'Password Length repartition',
        'section_most': 'Top 10 Most used passwords',
        'section_baseword': 'Top 10 Most used basewords',
        'section_mask': 'Top 10 Most used masks',
        'legend': 'Legend: d = digit, l = lowercase, U = uppercase, $ = special',
        'section_history': 'Users with similar password pattern along history',
        'footer_prefix': 'Report generated with',
        'format_header': 'Format',
        'count_header': 'Count',
        'length_header': 'Length',
        'password_header': 'Password',
        'mask_header': 'Masks',
        'percent_header': 'Percent',
        'xlabel_length': 'Length',
        'ylabel_count': 'Count',
        'history_with': 'Users with similar password \npattern along history',
        'history_without': 'Users without similar password \npattern along history',
    },
    'fr': {
        'lang_code': 'fr',
        'page_title': 'Rapport de craquage de mots de passe',
        'title': 'Rapport de craquage de mots de passe',
        'total_hashes': 'Nombre total de hachages soumis :',
        'passwords_found': 'Mots de passe trouvés :',
        'passwords_not_found': 'Mots de passe non trouvés :',
        'percent_recovered': 'Pourcentage de mots de passe récupérés :',
        'section_format': 'Répartition du format des mots de passe',
        'section_length': 'Répartition de la longueur des mots de passe',
        'section_most': 'Top 10 des mots de passe les plus utilisés',
        'section_baseword': 'Top 10 des mots racines les plus utilisés',
        'section_mask': 'Top 10 des masques les plus utilisés',
        'legend': 'Légende : d = chiffre, l = minuscule, U = majuscule, $ = spécial',
        'section_history': 'Utilisateurs avec un mot de passe similaire dans l’historique',
        'footer_prefix': 'Rapport généré avec',
        'format_header': 'Format',
        'count_header': 'Nombre',
        'length_header': 'Longueur',
        'password_header': 'Mot de passe',
        'mask_header': 'Masques',
        'percent_header': 'Pourcentage',
        'xlabel_length': 'Longueur',
        'ylabel_count': 'Nombre',
        'history_with': 'Utilisateurs ayant un mot de passe \nsimilaire dans l’historique',
        'history_without': 'Utilisateurs sans mot de passe \nsimilaire dans l’historique',
    },
}

TEMPLATE = '''<!DOCTYPE html>
<html lang="{{lang_code}}">
    <head>
        <meta charset="UTF-8">
        <title>{{page_title_text}}</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background-color: #f7f7f7; color: #333; }
            table { border-collapse: collapse; margin-bottom: 20px; width: 100%; background-color: #fff; }
            th, td { border: 1px solid #ccc; padding: 8px 12px; }
            th { background-color: #e9e9e9; }
            tr:nth-child(even) { background-color: #f2f2f2; }
            h1 { text-align: center; }
            img { max-width: 100%; height: auto; }
            .chart { width: 800px; display: block; margin: 0 auto; }
        </style>
    </head>
    <body>
            <h1>{{title_text}}</h1>
            <br>
            <p>{{total_hashes}} <b>{{total_user}}</b></p>
            <p>{{passwords_found}} <b>{{cracked}}</b></p>
            <p>{{passwords_not_found}} <b>{{not_cracked}}</b></p>
            <p>{{percent_recovered}} <b>{{cracked_pct}}%</b></p>
            <br>
            <img src='{{img_found}}' class="chart">
            <br>
            <h3 id="format">{{section_format}}</h3>
            <table>
                <thead>
                    <tr>
                        <th scope="col">{{format_header}}</th>
                        <th scope="col">{{count_header}}</th>
                    </tr>
                </thead>
                <tbody>
                    {% for format,count in format.items() %}
                    <tr>
                        <td>{{format}}</td>
                        <td>{{count}}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            <br>
            <img src='{{img_format}}' class="chart">
            <br>
            <h3 id="length">{{section_length}}</h3>
            <table>
                <thead>
                    <tr>
                        <th scope="col">{{length_header}}</th>
                        <th scope="col">{{count_header}}</th>
                    </tr>
                </thead>
                <tbody>
                    {% for top,count in length.items() %}
                    <tr>
                        <td>{{top}}</td>
                        <td>{{count}}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            <br>
            <div class="crop-container">
                <img src='{{img_length}}' class="chart">
            </div>
            <br>
            <h3 id="most">{{section_most}}</h3>
            <table>
                <thead>
                    <tr>
                        <th scope="col">{{password_header}}</th>
                        <th scope="col">{{count_header}}</th>
                    </tr>
                </thead>
                <tbody>
                    {% for top,count in most.items() %}
                    <tr>
                        <td>{{top}}</td>
                        <td>{{count}}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            <br>
            <div class="crop-container">
                <img src='{{img_most}}' class="chart">
            </div>
            <br>
            <br>
            <h3 id="baseword">{{section_baseword}}</h3>
            <table>
                <thead>
                    <tr>
                        <th scope="col">{{password_header}}</th>
                        <th scope="col">{{count_header}}</th>
                    </tr>
                </thead>
                <tbody>
                    {% for top,count in baseword.items() %}
                    <tr>
                        <td>{{top}}</td>
                        <td>{{count}}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            <br>
            <div class="crop-container">
                <img src='{{img_baseword}}' class="chart">
            </div>
            <br>
            <h3 id="mask">{{section_mask}}</h3>
            <table>
                <thead>
                    <tr>
                        <th scope="col">{{mask_header}}</th>
                        <th scope="col">{{count_header}}</th>
                        <th scope="col">{{percent_header}}</th>
                    </tr>
                </thead>
                <tbody>
                    {% for top,count in masks.items() %}
                    <tr>
                        <td>{{top}}</td>
                        <td>{{count}}</td>
                        <td>{{ '%.2f'| format(count/cracked*100) }}%</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            <br>
            <p>{{legend}}</p>
            <br>
            {% if img_history != '' %}
                <h3 id="history">{{section_history}}</h3>
                <br>
                <div class="crop-container">
                <img src='{{img_history}}' class="chart">
                </div>
                <br>
            {% endif %}
            <span id=footer>{{footer_prefix}} <a href="https://github.com/wodensec/graphcat-ng">https://github.com/wodensec/graphcat-ng</a>, a tool originally by <a href="https://github.com/Orange-Cyberdefense/graphcat">Orange Cyberdefense</a>.</span>
    </body>
</html>
'''

class Secret:
    def __init__(self, nthash: str, cleartext: str = None):
        self.nthash = nthash

        self.cleartext = cleartext
        self.cracked = (cleartext is not None)

    def define_cleartext(self, cleartext):
        self.cracked = True
        self.cleartext = cleartext

class User:
    def __init__(self, username: str, nthash: str, cleartext: str = None):
        self.username = username

        self.secret = Secret(nthash, cleartext)
        self.cracked = (cleartext is not None)

        self.history = None

    def add_into_history(self, index: int, nthash: str, cleartext:str = None) -> None:
        if self.history is None:
            self.history = dict()
        
        self.history[index]=Secret(nthash, cleartext)

    def define_cleartext(self, cleartext: str) -> None:
        self.cracked = True
        self.secret.define_cleartext(cleartext)

class GraphCat:
    def __init__(self, options):
        self.options = options
        self.trans = TRANSLATIONS['fr'] if self.options.french else TRANSLATIONS['en']

        self.timestamp = calendar.timegm(time.gmtime())
        self.potfile = None
        self.hashes = None
        self.outputdir = '.'
        if self.options.output_dir is not None:
            self.outputdir = self.options.output_dir
            if not os.path.isdir(self.outputdir):
                os.makedirs(self.outputdir, exist_ok=True)

        print('[-] Parsing potfile')
        if self.options.potfile is not None:
            arr = dict()
            with open(self.options.potfile, 'r') as lines:
                for line in lines:
                    l = line.rstrip('\n')
                    if ':' in l:
                        l = l.split(':',1)
                        arr[l[0].lower()]=l[1]
                self.potfile = arr
        if len(self.potfile) == 0:
            print('[!] No entry in potfile. Exiting...')
            sys.exit(1)
        print('[-] %s entries in potfile' % len(self.potfile))

        print('[-] Parsing hashfile')
        if self.options.hashfile is not None:

            with open(self.options.hashfile, 'r') as lines:
                if self.options.format in ['1','2']:
                    self.hashes = [line.rstrip('\n') for line in lines ]
                elif self.options.format == '3':
                    self.hashes = [line.rstrip('\n').split(':::')[0] for line in lines
                    if '$:' not in line and '$_history' not in line and ':::' in line]
                else:
                    print('[!] Unknown format')
                    sys.exit(1)
        if len(self.hashes) == 0:
            print('[!] No entry in hashfile. Exiting...')
            sys.exit(1)
        print('[-] %s entries in hashfile' % len(self.hashes))

        self._users = None
        self._cracked_users = None
        self._user_and_nt_dict = None
        self._all_nt_hash = None

    def gen_stat(self) -> Dict:
        print('[-] Generating graphs...')

        dirpath = os.path.join(self.outputdir, f"results_{self.timestamp}")
        if not os.path.exists(dirpath):
            os.makedirs(dirpath, exist_ok=True)
        
        print(f"Results directory: {dirpath}")
        
        # Pie N°1 : Cracked stats

        total_user = len(self.all_nt_hash)

        found = dict()

        if len(self.cracked_users) < 1 :
            print('[!] Not user cracked ! Exiting...')
            sys.exit(0)

        found['Recovered'] = len(self.cracked_users)
        found['Not recovered'] = total_user - len(self.cracked_users)

        cracked_pct = str(round(((int(found['Recovered']) / total_user) * 100), 2))

        plt.clf()
        plt.figure(figsize=[15, 7])
        text_prop = {
            'fontsize': 20,
            'fontweight': 'heavy',
            'color': 'black',
        }

        plt.pie(found.values(),
                wedgeprops={'edgecolor':'White','linewidth': 5,'antialiased': True},
                textprops=text_prop,
                colors = ['#DC1215', '#07C136'],
                startangle=90,
                autopct='%.1f%%',
                pctdistance=1.3,
                )
        
        plt.legend(labels=found.keys(), loc='best', 
           bbox_to_anchor=(0.,0.2), ncol=1, fontsize=16)

        centre_circle = plt.Circle((0, 0), 0.60, fc='white')
        fig = plt.gcf()
        fig.gca().add_artist(centre_circle)

        plt.savefig(os.path.join(dirpath,'cracked.png'), dpi=118)
        if self.options.export_charts:
            print('[-] Cracked charts available at cracked.png')
            plt.savefig(os.path.join(self.outputdir,'cracked.png'), dpi=118)

        # Pie N°2 : Format

        format = dict()

        format['Empty'] = len([e[0] for e in self.cracked_users.items() if e[1] == ''])
        format['Numeric'] = len([e[0] for e in self.cracked_users.items() if re.match('^[0-9]+$',e[1])])
        format['Alpha'] = len([e[0] for e in self.cracked_users.items() if re.match('^[a-zA-Z]+$',e[1])])
        format['Alpha + Numeric'] = len([e[0] for e in self.cracked_users.items() if re.match('^(?=[a-zA-Z0-9]*[0-9])(?=[a-zA-Z0-9]*[a-z])(?=[a-zA-Z0-9]*[A-Z])[a-zA-Z0-9]+$',e[1])])
        format['Alpha + Special'] = len([e[0] for e in self.cracked_users.items() if re.match('^(?=[a-zA-Z!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]*[a-z])(?=[a-zA-Z!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]*[A-Z])(?=[a-zA-Z!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]*[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?])[a-zA-Z!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]+$',e[1])])
        format['Numeric + Special'] = len([e[0] for e in self.cracked_users.items() if re.match('^(?=[0-9!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]*[0-9])(?=[0-9!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]*[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?])[0-9!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]+$',e[1])])
        format['Alpha + Numeric + Special'] = len([e[0] for e in self.cracked_users.items() if re.match('^(?=[a-zA-Z0-9!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]*[0-9])(?=[a-zA-Z0-9!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]*[a-z])(?=[a-zA-Z0-9!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]*[A-Z])(?=[a-zA-Z0-9!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]*[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?])[a-zA-Z0-9!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]+$',e[1])])

        else_format = 0 # Merging every format with less than 1% into 'Other' category 
        for val in format.values(): 
            if val < (found['Recovered']/100):
                else_format += val

        tmp_format = {f'{key}: {val}':val for key, val in format.items() if val > 0 and val > (found['Recovered']/100)}
        if else_format > 0:
            tmp_format[f'Other: {else_format}'] = else_format
        
        plt.clf()
        plt.figure(figsize=[15, 7])
        text_prop = {
            'fontsize': 20,
            'fontweight': 'heavy',
            'color': 'black',
        }
        
        plt.pie(tmp_format.values(),
                wedgeprops={'edgecolor':'White','linewidth': 5,'antialiased': True},
                textprops=text_prop,
                )
        
        plt.legend(labels=tmp_format.keys(), loc='best', 
           bbox_to_anchor=(0.,0.6), ncol=1, fontsize=16)

        centre_circle = plt.Circle((0, 0), 0.60, fc='white')
        fig = plt.gcf()
        fig.gca().add_artist(centre_circle)

        plt.savefig(os.path.join(dirpath,'format.png'), dpi=118)
        if self.options.export_charts:
            print('[-] Password format repartition available at format.png')
            plt.savefig(os.path.join(self.outputdir,'format.png'), dpi=118)

        # Pie N°3 : Length repartition

        longueur = dict()

        longueur['0-5'] = len([e[0] for e in self.cracked_users.items() if re.match('^.{0,5}$',e[1])])
        longueur['6'] = len([e[0] for e in self.cracked_users.items() if re.match('^.{6}$',e[1])])
        longueur['7'] = len([e[0] for e in self.cracked_users.items() if re.match('^.{7}$',e[1])])
        longueur['8'] = len([e[0] for e in self.cracked_users.items() if re.match('^.{8}$',e[1])])
        longueur['9'] = len([e[0] for e in self.cracked_users.items() if re.match('^.{9}$',e[1])])
        longueur['10'] = len([e[0] for e in self.cracked_users.items() if re.match('^.{10}$',e[1])])
        longueur['11'] = len([e[0] for e in self.cracked_users.items() if re.match('^.{11}$',e[1])])
        longueur['12'] = len([e[0] for e in self.cracked_users.items() if re.match('^.{12}$',e[1])])
        longueur['13'] = len([e[0] for e in self.cracked_users.items() if re.match('^.{13}$',e[1])])
        longueur['14'] = len([e[0] for e in self.cracked_users.items() if re.match('^.{14}$',e[1])])
        longueur['15+'] = len([e[0] for e in self.cracked_users.items() if re.match('^.{15,}$',e[1])])

        longueur_max = max(longueur.values())

        plt.clf()
        x = longueur.keys()
        y = list(longueur.values())
        plt.figure(figsize=[15, 7])
        plt.bar(x,y,  color='#3563EC', edgecolor='white')
        plt.xlabel(self.trans['xlabel_length'], fontsize=20)
        plt.ylabel(self.trans['ylabel_count'], fontsize=20)
        plt.rc('axes', titlesize=20)
        plt.rc('font', size=15)
        plt.xticks(fontsize=15)
        plt.yticks(fontsize=15)
        for i in range(len(x)):
            plt.text(i, y[i]+(longueur_max/100*1.5), y[i], ha = 'center')
        plt.savefig(os.path.join(dirpath,'length.png'), dpi=118)
        if self.options.export_charts:
            print('[-] Password length repartition available at length.png')
            plt.savefig(os.path.join(self.outputdir,'length.png'), dpi=118)

        # Pie N°4 and N°5 : Top 10 most cracked and Top 10 basewords

        c = Counter()
        c2 = Counter()
        c3 = Counter()
        for password in self.cracked_users.values():
            for i in re.findall('[a-zA-Z]{4,20}', password):
                c2[i] += 1
            if password == '':
                password = '[VIDE]'
            c[password] += 1
            c3[self.gen_mask(password)] +=1
        
        most = dict()
        for most_common in c.most_common(10):
            most[most_common[0]] = most_common[1]

        most_max = max(most.values())

        most = {key:val for key, val in most.items() if val >1}

        plt.clf()
        x = [label.replace('$$','\\$\\$') for label in most.keys()]
        y = list(most.values())
        plt.figure(figsize=[15, 10])
        plt.bar(x,y, color='#3563EC', edgecolor='white')
        plt.ylabel(self.trans['ylabel_count'], fontsize=20)
        plt.xticks(rotation=23)
        for i in range(len(x)):
            plt.text(i, y[i]+(most_max/100*1.5), y[i], ha = 'center')
        plt.savefig(os.path.join(dirpath,'most.png'), dpi=118)
        if self.options.export_charts:
            print('[-] Top10 most cracked password at most.png')
            plt.savefig(os.path.join(self.outputdir,'most.png'), dpi=118)

        basewords = dict()
        for key, value in c2.most_common(10):
            basewords[key] = value

        baseword_max = max(basewords.values())

        basewords = {key:val for key, val in basewords.items() if val >1}
        plt.clf()
        x = basewords.keys()
        y = list(basewords.values())
        plt.figure(figsize=[15, 10])
        plt.bar(x,y, color='#3563EC', edgecolor='white')
        plt.ylabel(self.trans['ylabel_count'],  fontsize=20)
        plt.xticks(rotation=23)
         
        for i in range(len(x)):
            plt.text(i, y[i]+(baseword_max/100*1.5), y[i], ha = 'center')
        plt.savefig(os.path.join(dirpath,'basewords.png'), dpi=118)
        if self.options.export_charts:
            print('[-] Top10 basewords at basewords.png')
            plt.savefig(os.path.join(self.outputdir,'basewords.png'), dpi=118)

        common_masks = dict()
        for key, value in c3.most_common(10):
            common_masks[key] = value

        # Chart N°7 Password same as in password history

        history_reuse = self.analyze_history()
        if history_reuse > 0:
            plt.clf()
            plt.figure(figsize=[15, 7])
            text_prop = {
                'fontsize': 20,
                'fontweight': 'heavy',
                'color': 'black',
            }
            plt.pie([history_reuse, len(self.cracked_users.values()) - history_reuse], 
                    wedgeprops={'edgecolor':'White','linewidth': 5,'antialiased': True},
                    textprops=text_prop,
                    colors = ['#DC1215', '#07C136'],
                    startangle=90,
                    autopct='%.1f%%',
                    pctdistance=1.3,
                    )

            plt.legend(labels=[self.trans['history_with'], self.trans['history_without']], loc='best',
            bbox_to_anchor=(0.1,0.2), ncol=1, fontsize=16)

            centre_circle = plt.Circle((0, 0), 0.60, fc='white')
            fig = plt.gcf()
            fig.gca().add_artist(centre_circle)

            plt.savefig(os.path.join(dirpath,'history.png'), dpi=118)
            if self.options.export_charts:
                print('[-] History analysis at history.png')
                plt.savefig(os.path.join(self.outputdir,'history.png'), dpi=118)
            
        # Generate pdf report based on htlm template
        print('[-] Generating report...')

        with open(os.path.join(dirpath, 'template.html'), 'w') as template:
            template.write(TEMPLATE)

        env = Environment(loader=FileSystemLoader(dirpath))

        template = env.get_template('template.html')

        html = template.render(page_title_text=self.trans['page_title'],
                            title_text=self.trans['title'],
                            lang_code=self.trans['lang_code'],
                            total_hashes=self.trans['total_hashes'],
                            passwords_found=self.trans['passwords_found'],
                            passwords_not_found=self.trans['passwords_not_found'],
                            percent_recovered=self.trans['percent_recovered'],
                            section_format=self.trans['section_format'],
                            format_header=self.trans['format_header'],
                            count_header=self.trans['count_header'],
                            section_length=self.trans['section_length'],
                            length_header=self.trans['length_header'],
                            section_most=self.trans['section_most'],
                            password_header=self.trans['password_header'],
                            section_baseword=self.trans['section_baseword'],
                            section_mask=self.trans['section_mask'],
                            mask_header=self.trans['mask_header'],
                            percent_header=self.trans['percent_header'],
                            legend=self.trans['legend'],
                            section_history=self.trans['section_history'],
                            footer_prefix=self.trans['footer_prefix'],
                            total_user = total_user,
                            cracked = found['Recovered'],
                            not_cracked = found['Not recovered'],
                            cracked_pct = cracked_pct,
                            format = format,
                            length = longueur,
                            most = most,
                            baseword = basewords,
                            masks = common_masks,
                            img_found = 'cracked.png',
                            img_format = 'format.png',
                            img_length = 'length.png',
                            img_most = 'most.png',
                            img_baseword = 'basewords.png',
                            img_masks =  'masks.png',
                            img_history = 'history.png' if history_reuse > 0 else '',
                            )

        with open(os.path.join(dirpath,'report.html'), 'w') as f:
            f.write(html)  

    def isNaN(self,num):
        return num!= num

    def gen_mask(self, password) -> str:
        mask = ""
        for letter in password:
            if letter in string.digits:
                mask += 'd'
            elif letter in string.ascii_lowercase:
                mask += 'l'
            elif letter in string.ascii_uppercase:
                mask += 'U'
            else:
                mask += '$'
        return mask
    
    def analyze_words(self, word1, word2):
        max_chain_similarity = 0
        similarity = 0
        for li in difflib.ndiff(word1, word2):
                    if li[0] == ' ':
                        similarity += 1
                    else:
                        similarity = 0
                    if similarity > max_chain_similarity:
                        max_chain_similarity = similarity
        return max_chain_similarity

    def analyze_history(self):
        pass_reuse_counter = 0
        for user in [user for user in self.users.values() if user.cracked]:
            if user.history is None:
                continue
            for hist in [hist for hist in user.history.values() if hist.cracked]:
                similitudes_len = self.analyze_words(hist.cleartext, user.secret.cleartext)
                if (similitudes_len >= 5) or (similitudes_len > len(user.secret.cleartext)-3) : # nearly same password (3 chars diff), or 5+ same chars in a row
                    pass_reuse_counter += 1
                    break
        return pass_reuse_counter

    def parse_ntds_line(self, line):
        elements = line.split(':')
        return elements[0], elements[3].lower() 

    @property
    def users(self) -> Dict:
        if self._users is not None:
            return self._users
        
        users = dict()
        userhist_lines = list()

        if self.options.format == '1':
            i = 0
            for hash in self.hashes:
                cleartext = None
                if hash in self.potfile.keys():
                    hash = hash.lower()
                    cleartext = self.potfile[hash]
                users[f'user_{i}']=User(f'user_{i}', hash, cleartext)
                i += 1
        elif self.options.format == '2':
            for line in self.hashes:
                username, hash = line.split(':')
                hash = hash.lower()
                cleartext = None
                if hash in self.potfile.keys():
                    cleartext = self.potfile[hash]
                users[username]=User(username, hash, cleartext)
        elif self.options.format == '3':
            for line in self.hashes:
                if '_history' in line:
                    userhist_lines.append(line)
                else:
                    username, nthash = self.parse_ntds_line(line)
                    cleartext = None
                    if nthash in self.potfile.keys():
                        cleartext = self.potfile[nthash]
                    users[username] = User(username, nthash, cleartext)
                    
            for userhist_line in userhist_lines:
                username, nthash = self.parse_ntds_line(userhist_line)
                user, index = username.split('_history')
                cleartext = None
                if nthash in self.potfile.keys():
                    cleartext = self.potfile[nthash]
                users[user].add_into_history(index, nthash, cleartext)

        self._users = users
        return self._users

    @property
    def cracked_users(self) -> Dict:
        if self._cracked_users is not None:
            return self._cracked_users
            
        self._cracked_users = {user.username:user.secret.cleartext for user in self.users.values() if user.cracked}
        return self._cracked_users

    @property
    def all_nt_hash(self) -> List:
        if self._all_nt_hash is not None:
            return self._all_nt_hash
        self._all_nt_hash = [user.secret.nthash for user in self.users.values()]
        return self._all_nt_hash

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(
        description="Password Cracking Graph Reporting", add_help=True
    )

    parser.add_argument(
        "-p", "--potfile",
        action="store",
        required=True,
        metavar="hashcat.potfile",
        help="Hashcat potfile",
    )

    parser.add_argument(
        "-H", "--hashfile",
        action="store",
        required=True,
        metavar="hashfile.txt",
        help="File containing hashes (one per line)",
    )

    parser.add_argument(
        "-f", "--format",
        action="store",
        default="3",
        help=(
            "hashfile format (default 3): 1 for hash; 2 for username:hash; "
            "3 for secretsdump (username:uid:lm:ntlm)"
        ),
    )
    parser.add_argument("--french", action="store_true", help="Generate report in French")
    parser.add_argument("-e", "--export-charts", action="store_true", help="Output also charts in png")
    parser.add_argument("-o", "--output-dir", action="store", help="Output directory")
    parser.add_argument("-d", "--debug", action="store_true", help="Turn DEBUG output ON")

    options = parser.parse_args()

    try:
        executor = GraphCat(options)
        executor.gen_stat()
    except Exception as e:
        if options.debug:
            import traceback
            traceback.print_exc()
        print('ERROR: %s' % str(e))
