const data=require('./addressbook.json');
const {contacts}=data
Object.entries(contacts).forEach(function([key, value]) {
    console.log(key, value);
})

Object.keys(contacts).forEach(function(key) {
    console.log(key, data.contacts[key]);
});

for (let key in contacts) {
    if (data.contacts.hasOwnProperty(key)) {
        console.log(key, data.contacts[key]);
    }
}
// node task.js