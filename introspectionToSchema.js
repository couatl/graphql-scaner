const graphql = require("graphql");
const fs = require('fs');
const { exec } = require('child_process');
const schemaPath = 'graphql/schema.graphql';

async function getSchemaGql() {
    try {
        if (fs.existsSync(schemaPath)) {
            return;
        }
    } catch (err) {}

    const rawdata = await fs.readFileSync('graphql/schema.json');
    const schema = JSON.parse(rawdata);

    const clientSchema = graphql.buildClientSchema(schema.data);
    const schemaString = graphql.printSchema(clientSchema);

    await fs.writeFile(schemaPath, schemaString, function (err) {
        if (err) return console.log(err);
        console.log('Schema > schema.graphql');
    });
}

async function generateQueries() {
    const queriesGenPath = 'graphql/queries_output';
    const gqlgCommand = `gqlg --schemaFilePath ${schemaPath} --destDirPath ${queriesGenPath} --depthLimit 5`;

    await exec(gqlgCommand, (err, stdout, stderr) => {
        if (err) {
            console.log(err);

            return;
        }

        // the *entire* stdout and stderr (buffered)
        console.log(`stdout: ${stdout}`);
        console.log(`stderr: ${stderr}`);
    });
}

getSchemaGql().then(() => {
    return generateQueries();
}).then(() => {
    console.log('Queries generation finished');
});
