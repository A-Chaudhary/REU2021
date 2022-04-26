from tqdm.notebook import tqdm as tqdm
import time
print(tqdm)


from py2neo import Graph, Node, Relationship, Subgraph #,  NodeMatcher
import csv
import re
import json


def startCell():
    global graph
    global update_nodes
    global nodes
    global relationships
    graph = Graph("http://localhost:7474", auth=("neo4j", "password"))
    update_nodes=[]
    nodes=[]
    relationships=[]


graph = None
update_nodes = None
nodes = None
relationships = None



startCell()
# graph.delete_all()
# size = 21111
size = 100000000
batch_size = 1000
# size = 44476
# size = 710
# size = 1000
# sleepValue = 90
sleepValue = 0.1


def batchUpdate():
    global update_nodes
    global nodes
    global relationships
    if(len(update_nodes) != 0):
        tx = graph.begin()
        update_nodes=Subgraph(nodes = update_nodes)
        tx.push(update_nodes)
        graph.commit(tx)
        update_nodes = []
    if(len(nodes) !=0):
        tx = graph.begin()
        nodes=Subgraph(nodes = nodes)
        tx.create(nodes)
        graph.commit(tx)
        nodes = []
        # print(len(relationships))
    if(len(relationships) != 0):
        tx = graph.begin()
        relationships=Subgraph(relationships = relationships)
        tx.create(relationships)
        graph.commit(tx)
        relationships = []



startCell()
dict_fdc = {}

csv_file = open('data/food.csv', 'r', encoding='utf-8-sig')
food_dict = csv.DictReader(csv_file)

index = 0

for row in tqdm(food_dict):
    if index > size:
        break
    food_node = Node("Food",description=row['description'], fdc_id=row['fdc_id'], data_type=row['data_type'],  publication_date=row['publication_date'])
    nodes.append(food_node)
    dict_fdc.update({row['fdc_id']:food_node})
    index+=1
    if(index % batch_size == 0):
        batchUpdate()
batchUpdate()


time.sleep(sleepValue)


def ingredientCleanUp():
    global ingredients

    ingredients=ingredients.upper() 

    ingredients = re.split("(\:|\(|\)|\[|\])|\; |\- |\.|\, |\,|\*|\*\*|\;|AND/OR|AND|\"\"", ingredients)
    ingredients = [j.strip() for j in ingredients if j] 
    # print(ingredients)
    # print('')

    i = 0
    while i < len(ingredients):
        if ingredients[i] is None:
            del ingredients[i]
            i -=1
        # print(ingredients[i] + " "+ str(i))
        if ingredients[i] == ':':
            # print('Deleted '+ str(i) + " " + str(ingredients[i]))
            del ingredients[i]
            # print('Deleted '+ str(i-1) + " " + str(ingredients[i-1]))
            del ingredients[i-1]
            # print(ingredients)
            i-=2
            # print("Next to be tested is " + str(ingredients[i+1]))
            # print("I is now " + str(i))
            # print("I'th position is now " + str(ingredients[i]) )
            
            # print(ingredients)
        i +=1
    ingredients = [j.strip() for j in ingredients if j] 
    # print(ingredients)
    # print('')


def listSplit(input_ingredient:str,input_val):
    output = []

    
    # print('     Append: ')
    # print(input_val)
    break_count = 0
    
    for i,entry in enumerate(input_val):
        
        if entry is None:
            continue
        # print(entry)
        # print(break_count)
        if entry == '(' or entry == '[':
            
            if break_count == 0:
                main_ingredient = ingredients[i-1].strip()
                break_start_index = i+1
                if ingredient == '(':
                    out_break = ')'
                else:
                    out_break = ']'
            break_count +=1
            # print(break_count)
            
        elif entry == ')' or entry == ']':
            break_count -=1
            if break_count == 0:
                sub_ingredient = (input_val[break_start_index:i])
                # print('Sub ing: '+ sub_ingredient)
                output.append( listSplit(main_ingredient, sub_ingredient) )
        elif break_count == 0: #str & str
            # print('Break Count is ' + str(break_count))
            if ', ' in entry:
                # print('     Entry')
                # print(entry)
                output = output +  re.split('\, ', entry.strip())
                # print(re.split('\, ', entry.strip()))
            else:
                output.append(entry)
    return output


    



startCell()
csv_file = open('data/branded_food.csv', 'r', encoding='utf-8-sig')
branded_food_dict = csv.DictReader(csv_file)
parsed_ingredient_dict = {}
index = 0

for row in tqdm(branded_food_dict):
    # if index < 3:
    #     index+=1
    #     continue
    if index > size:
        break
    try:
        food_node = dict_fdc[row['fdc_id']]
    except:
        food_node = None
    if (food_node):
        if(row['ingredients']):
            # print(row['ingredients'])
            ingredients = row['ingredients']
            ingredients_2 = []
            break_count = 0
            
            

            ingredientCleanUp()

            for i, ingredient in enumerate(ingredients):    
                if ingredient == '(' or ingredient == '[':
                    if break_count == 0:
                        main_ingredient = ingredients[i-1].strip()
                        break_start_index = i+1
                        if ingredient == '(':
                            out_break = ')'
                        else:
                            out_break = ']'
                    break_count +=1
                    continue
                elif ingredient == ')' or ingredient == ']':
                    break_count -=1
                    if break_count == 0 and ingredient == out_break:
                        # print('     Main Ingredient: ' + main_ingredient)
                        sub_ingredient = (ingredients[break_start_index:i])
                        # print('     ' + str(sub_ingredient))
                        ingredients_2.append( listSplit(main_ingredient, sub_ingredient) )
                    continue
                elif break_count == 0: #If Not in a list of ingredients for a main ingredient
                    # print('Added ' + str(ingredients[i]))
                    ingredients_2.append(ingredients[i])

            parsed_ingredient_dict.update({row['fdc_id']:ingredients_2})
            # print(ingredients_2)
            # print('---------------------------------------')
    else:
        # print(str(row['fdc_id']) +" Not Found")
        pass
    index+=1   


def makeIngredientConnections(previous_entry:str, value):
    global relationships
    # print(previous_entry)
    try:
        main_ingredient_node = dict_ingredients[previous_entry]
    except:
        main_ingredient_node = None
        # print(previous_entry)
        return
    for i,entry in enumerate(value):
        if isinstance(entry, list):
            try:
                makeIngredientConnections(value[i-1], entry)
            except:
                makeIngredientConnections(value[i-2], entry)
        else: #If Single Ingredient in Entry
            try: 
                ingredient_node = dict_ingredients[entry]
            except:
                ingredient_node = None
            if(not ingredient_node): 
                ingredient_node = Node("Ingredient",name=entry)
                nodes.append(ingredient_node)
                dict_ingredients.update({entry:ingredient_node})
            try:
                relation = dict_ingredients_relationships[(previous_entry, entry)]
                relation['weight'] +=1
            except:
                relation = Relationship(main_ingredient_node, "HAS_INGREDIENT", ingredient_node, weight=1)
                # relationships.append(relation)
            dict_ingredients_relationships.update({ (previous_entry, entry) : relation})
    


startCell()
index = 0
dict_ingredients = {}
dict_ingredients_relationships = {}

for (fdc_id, value) in tqdm(parsed_ingredient_dict.items()):
    if index > size:
        break
    try:
        food_node = dict_fdc[fdc_id]
        # print(dict_fdc[fdc_id])
    except:
        food_node = None
    if (food_node):
        for i, entry in enumerate(value):
            if isinstance(entry, list):
                try:
                    
                    makeIngredientConnections(value[i-1], entry)
                except:
                    print(value[i-1])
                    print("Value Above didnt work")
                    print(value[i-2])
                    makeIngredientConnections(value[i-2], entry)
                pass
            else:
                #If Single Ingredient in Entry
                try: 
                    ingredient_node = dict_ingredients[entry]
                except:
                    ingredient_node = None
                if(not ingredient_node): 
                    ingredient_node = Node("Ingredient",name=entry)
                    nodes.append(ingredient_node)
                    dict_ingredients.update({entry:ingredient_node})
                relation = Relationship(food_node, "HAS_INGREDIENT", ingredient_node, weight=1)
                relationships.append(relation)
    
    index+=1
    if(index % batch_size == 0):
        batchUpdate()
batchUpdate()



# Serialize data into file:
json.dump( dict_ingredients, open( "dict/dict_ingredients.json", 'w' ) )

dict_ingredients = {}

# Serialize data into file:
json.dump( parsed_ingredient_dict, open( "dict/dict_parsed_ingredient.json", 'w' ) )

parsed_ingredient_dict = {}




index = 0

for (key,value) in tqdm(dict_ingredients_relationships.items()):
    relationships.append(value)
    index +=1
    if(index % batch_size == 0):
        batchUpdate()
batchUpdate()
       
dict_ingredients_relationships = {}


time.sleep(sleepValue)


startCell()
dict_nutrients = {}

csv_file = open('data/food_nutrient.csv', 'r', encoding='utf-8-sig')
food_nutrient_dict = csv.DictReader(csv_file)

index = 0

for row in tqdm(food_nutrient_dict):
    if index > size:
        break
    try:
        food_node = dict_fdc[row['fdc_id']]
    except:
        food_node = None

    if(food_node):

        try:
            nutrient_node = dict_nutrients[row['nutrient_id']]
        except:
            nutrient_node = None
            pass

        if(nutrient_node == None):
            nutrient_node = Node("Nutrient", nutrient_id=row['nutrient_id'])
            nodes.append(nutrient_node)
            dict_nutrients.update({row['nutrient_id']:nutrient_node})
        relation = Relationship(food_node, "HAS_NUTRIENT", nutrient_node, amount=row['amount'])
        if(row['data_points']):
            relation.update(data_points=row['data_points'])
        if(row['min']):
            relation.update(min=row['min'])
        if(row['max']):
            relation.update(max=row['max'])
        if(row['median']):
            relation.update(median=row['median'])
        # graph.create(relation)
        relationships.append(relation)
    else:
        # print(str(row['fdc_id']) +" Not Found")
          pass
    index+=1

    if (index % batch_size == 0):
        batchUpdate()
batchUpdate()



time.sleep(sleepValue)


startCell()

dict_category = {}

csv_file = open('data/branded_food.csv', 'r', encoding='utf-8-sig')
branded_food_dict = csv.DictReader(csv_file)

index = 0

for row in tqdm(branded_food_dict):
    if index > size:
        break
    try:
        food_node = dict_fdc[row['fdc_id']]
    except:
        food_node = None
    if(food_node):
        # print(row['fdc_id'])
        food_node.update(brand_owner=row['brand_owner'])
        if(row['brand_name']):
            food_node.update(brand_name=row['brand_name'])
        if(row['subbrand_name']):
            food_node.update(subbrand_name=row['subbrand_name'])
        if(row['gtin_upc']):
            food_node.update(gtin_upc=row['gtin_upc'])     
        # if(row['ingredients']):
            # food_node.update(ingredients=row['ingredients']) 
        if(row['not_a_significant_source_of']):
            food_node.update(not_a_significant_source_of=row['not_a_significant_source_of'])
        if(row['serving_size']):
            food_node.update(serving_size=row['serving_size'])    
        if(row['serving_size_unit']):
            food_node.update(serving_size_unit=row['serving_size_unit'])
        if(row['branded_food_category']):
            branded_food_categories = row['branded_food_category'].split('  ') 
            for branded_food_category in branded_food_categories:
                try:
                    food_category_node = dict_category[row['branded_food_category']]
                except:
                    food_category_node = None
                    pass
                if(food_category_node== None):
                    food_category_node = Node("Branded_Food_Category", name=branded_food_category)
                    nodes.append(food_category_node)
                    dict_category.update({row['branded_food_category']:food_category_node})
                
                relation = Relationship(food_node, "IS_IN_BRANDED_FOOD_CATEGORY", food_category_node)
                relationships.append(relation)
        if (row['market_country']):
            food_node.update(market_country=row['market_country'])   

        # graph.push(food_node)
        update_nodes.append(food_node)
        dict_fdc[row['fdc_id']] = food_node
    else:
        print(str(row['fdc_id']) + " not found")
    index+=1
    if (index % batch_size == 0):
        batchUpdate()
batchUpdate()



time.sleep(sleepValue)


startCell()

csv_file = open('data/nutrient_incoming_name.csv', 'r', encoding='utf-8-sig')
food_nutrient_name_dict = csv.DictReader(csv_file)

index = 0

for row in tqdm(food_nutrient_name_dict):
    if index > size:
        break
    try:
            nutrient_node = dict_nutrients[row['nutrient_id']]
    except:
        nutrient_node = None
        pass
    if (nutrient_node):
        if(row['name']):
            if(nutrient_node['name']):
                nutrient_node['name'].append(row['name'])
            else:
                nutrient_node.update(name=[row['name'], ])
            update_nodes.append(nutrient_node)
            dict_nutrients[row['nutrient_id']] = nutrient_node
    index+=1
    if (index % batch_size == 0):
        batchUpdate()
batchUpdate()



# Serialize data into file:
json.dump( dict_nutrients, open( "dict/dict_nutrients.json", 'w' ) )
dict_nutrients = {}


time.sleep(sleepValue)


startCell()

csv_file = open('data/food_portion.csv', 'r', encoding='utf-8-sig')
food_portion_dict = csv.DictReader(csv_file)

csv_file = open('data/measure_unit.csv', 'r', encoding='utf-8-sig')
measure_unit_csv = csv.reader(csv_file)
next(measure_unit_csv)
measure_unit_dict = dict(measure_unit_csv)


index = 0

for row in tqdm(food_portion_dict):
    if index > size:
        break

    try:
        food_node = dict_fdc[row['fdc_id']]
    except:
        food_node = None
    if (food_node and not food_node['amount_measure']):
        if(row['amount'] and row['measure_unit_id']):
            food_node.update(amount_measure=(row['amount'] + " " + measure_unit_dict[ row['measure_unit_id'] ] ))
        if(row['modifier']):
            food_node.update(modifier=row['modifier'])
        if(row['gram_weight']):
            food_node.update(gram_weight=row['gram_weight'])
        if(row['data_points']):
            food_node.update(data_points=row['data_points'])
        update_nodes.append(food_node)
        dict_fdc[row['fdc_id']] = food_node
    index+=1
    if (index % batch_size == 0):
        batchUpdate()
batchUpdate()


time.sleep(sleepValue)


startCell()

csv_file = open('data/input_food.csv', 'r', encoding='utf-8-sig')
input_food_dict = csv.DictReader(csv_file)

index = 0


for row in tqdm(input_food_dict):
    if index > size:
        break
    try:
        food_node = dict_fdc[row['fdc_id']]
    except:
        food_node = None
        
    try:
        input_food_node = dict_fdc[row['fdc_id']]
    except:
        input_food_node = None

    if(food_node):
        if(input_food_node):
            relationships.append(Relationship(input_food_node, "IS_AN_INPUT_OF", food_node))
        else:
            print("Input Food " + str(row['fdc_of_input_food']) + " Not Found")
    else:
        # print("Food " + str(row['fdc_id']) + " Not Found")
        pass

    index+=1
    if (index % batch_size == 0):
        batchUpdate()
batchUpdate()


time.sleep(sleepValue)


startCell()

csv_file = open('data/food_calorie_conversion_factor.csv', 'r', encoding='utf-8-sig')
food_calorie_conversion_dict = csv.DictReader(csv_file)

csv_file = open('data/food_nutrient_conversion_factor.csv', 'r', encoding='utf-8-sig')
food_nutrient_conversion_csv = csv.reader(csv_file)
next(food_nutrient_conversion_csv)
food_nutrient_conversion_dict = dict(food_nutrient_conversion_csv)

index = 0

for row in tqdm(food_calorie_conversion_dict):
    if index > size:
        break
    try:
        food_node_fdc_id = food_nutrient_conversion_dict[row['food_nutrient_conversion_factor_id']]
    
        try:
            food_node = dict_fdc[food_node_fdc_id]
        except:
            food_node = None
        if (food_node):
            if(row['protein_value']):
                food_node.update(protein_value=row['protein_value'])
            if(row['fat_value']):
                food_node.update(fat_value=row['fat_value'])
            if(row['carbohydrate_value']):
                food_node.update(carbohydrate_value=row['carbohydrate_value'])    
            # graph.push(food_node)
            update_nodes.append(food_node)
            dict_fdc[row['fdc_id']] = food_node
            # print(food_node)
        else:
            # print("Food " + str(food_node_fdc_id) + " Not Found")
            pass
    except:
        # print("Food fdc_id " + str(row['food_nutrient_conversion_factor_id']) + " Not Found")
        pass
    index+=1
    if (index % batch_size == 0):
        batchUpdate()
batchUpdate()


# Serialize data into file:
json.dump( dict_fdc, open( "dict/dict_fdc.json", 'w' ) )


startCell()
graph.run("MATCH (i:Ingredient) SET i.degree = size( (i)<-[:HAS_INGREDIENT]-())")
graph.run("MATCH (i:Ingredient)<-[r:HAS_INGREDIENT]-() WITH i, sum(r.weight) AS weightedDegree SET i.weightedDegree = weightedDegree")


graph.run("MATCH (i:Ingredient) SET i.outDegree = size( (i)-[:HAS_INGREDIENT]->())")
graph.run("MATCH (i:Ingredient)-[r:HAS_INGREDIENT]->() WITH i, sum(r.weight) AS weightedOutDegree SET i.weightedOutDegree = weightedOutDegree")
graph.run("MATCH (i:Ingredient) WHERE NOT exists(i.weightedOutDegree) SET i.weightedOutDegree = 0 RETURN i.name, i.outDegree, i.weightedOutDegree")


graph.run("MATCH (b:Branded_Food_Category) SET b.degree = size( (b)<-[:IS_IN_BRANDED_FOOD_CATEGORY]-())")


graph.run("MATCH (f:Food) SET f.numOfIngredients = size((f)-[:HAS_INGREDIENT]->())")


graph.run("CALL gds.graph.create('myGraph','Ingredient','HAS_INGREDIENT',{relationshipProperties: 'weight'})")
graph.run(""" CALL gds.pageRank.stream('myGraph', {
  maxIterations: 1000,
  dampingFactor: 0.85,
  relationshipWeightProperty: 'weight'

})
YIELD nodeId, score
SET gds.util.asNode(nodeId).pageRankScore=score
""")
# graph.run("CALL gds.pageRank.stream('myGraph') YIELD nodeId, score SET gds.util.asNode(nodeId).pageRankScore=score RETURN gds.util.asNode(nodeId).name AS name, score ORDER BY score DESC, name ASC")


# graph.run("CALL gds.louvain.stream('myGraph') YIELD nodeId, communityId, intermediateCommunityIds SET gds.util.asNode(nodeId).louvainCommunityId = communityId RETURN gds.util.asNode(nodeId).name AS name, communityId, intermediateCommunityIds ORDER BY communityId DESC")


# # Test Out Weighted Louvain with 
graph.run(
"""CALL gds.louvain.stream('myGraph', { relationshipWeightProperty: 'weight', includeIntermediateCommunities: true })
YIELD nodeId, communityId, intermediateCommunityIds
SET gds.util.asNode(nodeId).weightedLouvainCommunityId = communityId, gds.util.asNode(nodeId).weightedLouvainIntermediateCommunityIds = intermediateCommunityIds
RETURN gds.util.asNode(nodeId).name AS name, communityId, intermediateCommunityIds
"""
)
# CALL gds.louvain.stream('myGraph', { relationshipWeightProperty: 'weight', includeIntermediateCommunities: true })
# YIELD nodeId, communityId, intermediateCommunityIds
# SET gds.util.asNode(nodeId).weightedLouvainCommunityId = communityId, gds.util.asNode(nodeId).weightedLouvainIntermediateCommunityIds = intermediateCommunityIds
# RETURN gds.util.asNode(nodeId).name AS name, communityId, intermediateCommunityIds
# ORDER BY name ASC



