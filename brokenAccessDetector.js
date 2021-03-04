const {GraphQLClient} = require('graphql-request');
const fs = require('fs');
const graphql = require("graphql");

const defaultValues = {
    'String': 'test_string',
    'ID': ['1', '"5ed496cc-c971-11dc-93cd-15767af24309"'],
    'Int': 1,
    'DateTime': '2021-07-09T11:54:42',
    'Date': '2021-07-09',
    'Float': 3.1415,
    'Boolean': true,
    'URI': "http://example.com/"
};

// TODO: Добавить справочник дефолтных значений
// stateful api testing

async function checkRequests(path) {
    const files = fs.readdirSync(path)
        .filter(file => file.includes('.gql'))
        .map(file => `${path}/${file}`);
    const vulnerableQueries = [];

    if (process.argv.length !== 3) {
        throw new 'You need to define GraphQL endpoint url as first argument!';
    }

    const [host] = process.argv.slice(2);

    for (file of files) {
        const query = fs.readFileSync(file, 'utf8');
        const parsed = graphql.parse(query);
        const variables = {};

        for (definition of parsed.definitions) {
            for (variable of definition.variableDefinitions) {
                try {
                    const variableName = variable.variable.name.value;
                    let variableType;

                    if (variable.type.name) {
                        variableType = variable.type.name.value;
                    } else if (variable.type.type) {
                        variableType = variable.type.type.name.value;
                    }

                    if (!defaultValues[variableType]) {
                        console.log('Not found placeholder value for ', variableType);

                        continue;
                    }

                    variables[variableName] = defaultValues[variableType];
                } catch (e) {
                    console.log('Found error on ', file, e);
                }
            }
        }


        const gql = new GraphQLClient(host);
        try {
            const data = await gql.request(query, variables);
        } catch (e) {
            console.log(`Checked query ${file} failed with error, continuing on others`);

            continue;
        }

        vulnerableQueries.push(file);
        console.log(`Found possibly vulnerable query ${file}`);
    }

    return vulnerableQueries;
}

async function checkQueries() {
    const queriesPath = 'graphql/queries_output/queries';

    try {
        fs.existsSync(queriesPath)
    } catch (err) {
        return;
    }

    return await checkRequests(queriesPath);
}

async function checkMutations() {
    const path = 'graphql/queries_output/mutations';

    try {
        fs.readdirSync(path)
    } catch (err) {
        console.log('No mutations found');

        return;
    }

    return await checkRequests(path);
}


async function requestQueries() {
    const queries = await checkQueries();
    const mutations = await checkMutations();

    if (queries && queries.length) {
        console.log(
            `Overall queries:
             ${queries.join('\n')}`
        );
    }

    if (mutations && mutations.length) {
        console.log(
            `Overall mutations:
             ${mutations.join('\n')}`
        );
    }
}

requestQueries().then(() => {
    console.log('Broken access control check finished')
});