const data=require('./addressbook.json');

Object.entries(data.contacts).forEach(function([key, value]) {
    console.log(key, value);
})

Object.keys(data.contacts).forEach(function(key) {
    console.log(key, data.contacts[key]);
});

for (let key in data.contacts) {
    if (data.contacts.hasOwnProperty(key)) {
        console.log(key, data.contacts[key]);
    }
}
// node task.js