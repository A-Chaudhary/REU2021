var driver = neo4j.driver(
    'neo4j://localhost:7687',
    neo4j.auth.basic('neo4j', 'password')
  );

var x;

var viz;
var initial_cypher;
var config;

var toggle;
var toggleNot="";
var index = 0;

var ingredient = 'GARLIC';



function initializeCypher(){
    initial_cypher = `
CALL {  CALL {
            MATCH (i:Ingredient)
            WHERE i.name CONTAINS "`+ ingredient.toString() + `"
            RETURN i
            ORDER BY i.pageRankScore DESC
            SKIP `+index.toString()+`
        }
        CALL {
            WITH i
            MATCH (i)<-[ra:HAS_INGREDIENT]-(fa:Food)
            RETURN ra,fa
            ORDER BY fa.numOfIngredients ASC
        }
        CALL {
            WITH i, fa
            MATCH (fa)-[ra2:HAS_INGREDIENT]->(ia2:Ingredient)
            WHERE `+toggleNot+` i.weightedLouvainCommunityId=ia2.weightedLouvainCommunityId AND NOT i=ia2 AND NOT ia2.name CONTAINS "`+ingredient.toString()+`" 
            RETURN ra2,ia2
            ORDER BY ia2.pageRankScore DESC
        }
        CALL {
            WITH i
            MATCH (i)<-[rd:HAS_INGREDIENT]-(fd:Food)
            RETURN rd,fd
            ORDER BY fd.numOfIngredients DESC
        }
        CALL {
            WITH i, fd
            MATCH (fd)-[rd2:HAS_INGREDIENT]->(id2:Ingredient)
            WHERE `+toggleNot+` i.weightedLouvainCommunityId=id2.weightedLouvainCommunityId AND NOT i=id2 AND NOT id2.name CONTAINS "`+ingredient.toString()+`" 
            RETURN rd2,id2
            ORDER BY id2.pageRankScore DESC
        }
        RETURN DISTINCT *
        LIMIT 100
        }
        RETURN * LIMIT 25
    `
}

function initalizeConfig() {
    config = {
        container_id: "viz",
        server_url: "bolt://localhost:7687",
        server_user: "neo4j",
        server_password: "password",
        labels: {
            "Ingredient": {
                "caption": "name",
                "size": "pageRankScore",
                // "size": "weightedDegree",
                "community": "weightedLouvainCommunityId"
                // "title_properties": [
                //     "name",
                //     "weightedDegree"
                // ]
            },
            "Branded_Food_Category": {
                "caption": "name",
                "size": "degree",
            },
            "Food": {
                "size": "numOfIngredients",
            },
        },
        relationships: {
            "HAS_INGREDIENT": {
                "thickness": "weight",
                "caption": false,
            },
            "IS_IN_BRANDED_FOOD_CATEGORY": {
                "caption": false,
            }
        },
        
        arrows: true,
        // console_debug: true,
        initial_cypher: initial_cypher
    };

}
async function draw() {
   initializeCypher();
   initalizeConfig();
    viz = new NeoVis.default(config);
    viz.render();
    toggle = 0;

    runQuery();
}

async function runQuery() {
    var driver = neo4j.driver(
        'neo4j://localhost',
        neo4j.auth.basic('neo4j', 'password')
    )
    const session = driver.session()
    
    try {
      const result = await session.run(`
      CALL {CALL {
        MATCH (i:Ingredient)
        WHERE i.name CONTAINS "`+ ingredient.toString() + `"
        RETURN i
        ORDER BY i.pageRankScore DESC
        SKIP `+index.toString()+`
    }
    CALL {
        WITH i
        MATCH (i)<-[ra:HAS_INGREDIENT]-(fa:Food)
        RETURN ra,fa
        ORDER BY fa.numOfIngredients ASC
    }
    CALL {
        WITH i, fa
        MATCH (fa)-[ra2:HAS_INGREDIENT]->(ia2:Ingredient)
        WHERE `+toggleNot+` i.weightedLouvainCommunityId=ia2.weightedLouvainCommunityId AND NOT i=ia2 AND NOT ia2.name CONTAINS "`+ingredient.toString()+`" 
        RETURN ra2,ia2
        ORDER BY ia2.pageRankScore DESC
    }
    CALL {
        WITH i
        MATCH (i)<-[rd:HAS_INGREDIENT]-(fd:Food)
        RETURN rd,fd
        ORDER BY fd.numOfIngredients DESC
    }
    CALL {
        WITH i, fd
        MATCH (fd)-[rd2:HAS_INGREDIENT]->(id2:Ingredient)
        WHERE `+toggleNot+` i.weightedLouvainCommunityId=id2.weightedLouvainCommunityId AND NOT i=id2 AND NOT id2.name CONTAINS "`+ingredient.toString()+`" 
        RETURN rd2,id2
        ORDER BY id2.pageRankScore DESC
    }
    RETURN DISTINCT ia2, id2
    LIMIT 100}
    RETURN * LIMIT 20
  `)
    var array = [];
      for (key in result.records) {
        node = result.records[key].get(0); 
        if (!(array.includes(node.properties.name)))  {
            array.push(node.properties.name);
        }
        node = result.records[key].get(1);
        if (!(array.includes(node.properties.name)))  {
            array.push(node.properties.name);
        }  
        
      }
    //   console.log("Printing Array");
    //   console.log(result.records);
    //   console.log(array);
    //   const singleRecord = result.records[0]
    //   const node = singleRecord.get(0)
    } finally {
      await session.close()
    }
    
    // on application exit:
    await driver.close()

    ul = document.createElement('ul');
    removeAllChildNodes(document.getElementById('list'))
    document.getElementById('list').appendChild(ul);

    array.forEach(function (item) {
        let li = document.createElement('li');
        ul.appendChild(li);

        li.innerHTML += item;
});
}

function removeAllChildNodes(parent) {
    while (parent.firstChild) {
        parent.removeChild(parent.firstChild);
    }
}



function toggleFunc() {
    if (toggle == 0) {
        config['labels']['Ingredient']['community'] = 'weightedLouvainIntermediateCommunityIds';
            viz.reinit(config);
            viz.render();
            toggle = 1;

    } else {
        config['labels']['Ingredient']['community'] = 'weightedLouvainCommunityId';
        viz.reinit(config);
        viz.render();
        toggle = 0;
    }

}

// function toggleNotFunc() {
//     if(toggleNot == ""){
//         toggleNot = "NOT"
//     }else {
//         toggleNot == ""
//     }
//     draw();

// }


function indexChange(change) {
    index += change;
    if (index < 0) {
        index = 0;
        return;
    }
    updateTitle();
    draw(); 
}




async function find() {
    ingredient = document.getElementById('inputText').value.toUpperCase()

    index=0;
    updateTitle();
    draw();
    

}

async function updateTitle() {
    var driver = neo4j.driver(
        'neo4j://localhost',
        neo4j.auth.basic('neo4j', 'password')
    )
    const session = driver.session()
    
    try {
      const result = await session.run(`
      
        MATCH (i:Ingredient)
        WHERE i.name CONTAINS "`+ ingredient.toString() + `"
        RETURN i
        ORDER BY i.pageRankScore DESC
        SKIP `+index.toString()+`
        LIMIT 1`
    )

    node = result.records[0].get(0);
    // console.log("node.properties.name");
    document.getElementById('ingredient').innerHTML = node.properties.name;
    
    } finally {
      await session.close()
    }
    // on application exit:
    await driver.close()
    // console.log(ingredient);
}


function search(ele) {
    if(event.key === 'Enter') {
        find()       
    }
}


