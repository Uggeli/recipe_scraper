from selenium import webdriver
import bs4
import time
import re
from multiprocessing import Pool
# import pandas as pd

# recipes = pd.DataFrame(columns=['ID', 'Title', 'CookingTime',
#                                 'Servings', 'Ingredients',
                                # 'CookingInstructions'])

unvisited_links = {}
visited_links = {}
url = 'http://www.kotikokki.net'

driver = webdriver.Chrome(executable_path=r'G:\Kdaus\pyyttoni\reseptikone\webdriver\chromedriver.exe')
driver.get('https://www.kotikokki.net/reseptit/')


def get_recipe(link):
    driver.get(link)

    source = driver.page_source
    soup = bs4.BeautifulSoup(source, 'lxml')
    try:
        name = soup.find('span', {'class': 'fn'}).text
    except:
        name = soup.find('h1', {'id': 'recipe-title'}).text
    else:
        pass
    try:
        cooking_time = soup.find('span', {'class': 'duration'}).text
    except:
        cooking_time = 'unknown'
    try:
        servings = soup.find('span', {'class': 'yield'}).text
    except:
        servings = 'unknown'

    ingredient_table = soup.find('table', {'class': 'list-ingredients'})
    ingredient_amounts = ingredient_table.find_all('span',
                                                   {'data-view-element':
                                                    ('amount',
                                                     'unit')})

    ingredients = ingredient_table.find_all('span',
                                            {'class': 'name'})

    ingredient_list = []
    x = 0
    y = 1
    for i, ingredient in enumerate(ingredients):
        ingredient_list.append(f'{ingredient_amounts[x].text} {ingredient_amounts[y].text} {ingredient.text}')
        x += 2
        y += 2

    instructions = soup.find('div', {'class': 'instructions'}).text

    return name, cooking_time, servings, ingredient_list, instructions


def get_links():
    source = driver.page_source
    soup = bs4.BeautifulSoup(source, 'lxml')
    muut_linkit = soup.find_all('a', href=True)
    for resepti in muut_linkit:
        linkki = resepti.get_attribute_list('href')[0]
        texti = resepti.text
        if 'resepti' in linkki:
            # print('==========')
            # print(f'{linkki}')
            try:
                resepti_num = re.search(r'([\d]+)', linkki)[0]
                if url not in linkki:
                    linkki = url + linkki
                    # print(linkki)
                if (resepti_num not in unvisited_links and
                        resepti_num not in visited_links):
                    unvisited_links[resepti_num] = linkki
            except:
                pass

i = 1
while True:
    driver.get(f'https://www.kotikokki.net/reseptit/?currentPage={i}')
    time.sleep(1)
    get_links()
    i += 1
    for recipe_num, link in unvisited_links.items():
        name, cooking_time, servings, ingredient_list, instructions = get_recipe(link)
        data = {'ID': recipe_num, 'Title': name, 'CookingTime': cooking_time,
                'Servings': servings, 'Ingredients': ingredient_list,
                'CookingInstructions': instructions}
        with open(fr'G:\Kdaus\pyyttoni\reseptikone\reseptit\{recipe_num}.txt',
                  'w', encoding='utf-8') as w:
            w.write(name.strip())
            w.write('\n')
            w.write(cooking_time.strip())
            w.write('\n')
            w.write(servings.strip())
            w.write('\n')
            for ingridient in ingredient_list:
                w.write(ingridient.strip())
                w.write('\n')
            w.write('\n')
            w.write(instructions.strip())

        # recipes = recipes.append(data, ignore_index=True)
        visited_links[recipe_num] = link
    unvisited_links.clear()
    if i > 50:
        break

# recipes.to_csv(r'G:\Kdaus\pyyttoni\reseptikone\testi.csv')


print(len(unvisited_links))

driver.quit()
