<script>    
    import { notification } from 'ant-design-vue';

    import Scheduler from "./Scheduler.vue"

    import ApiSupplicant from "../helpers/ApiSupplicant.vue"
    import DateTime from "../helpers/DateTime.vue"

    export default {
        mixins: [
            ApiSupplicant, DateTime
        ],
        components: { Scheduler },
        data() {
            return {
                groups: [],
                events: [],
                selectedGroupId: 0                
            };
        },
        async created () {
            await this.listGroups();
        },
        methods: {
            // **************************************************************************************************************************************************
            // Public
            // **************************************************************************************************************************************************

            async listGroups() {
                this.groups = await this.__listGroups();
            },

            async loadEvents(groupId) {
                this.selectedGroupId = groupId;
                this.events = await this.__listEvents(this.selectedGroupId);
            },

            async eventsUpdate(action, data) {
                if (this.selectedGroupId) {
                    try {
                        if (action == "create") {
                            this.events.push(data);
                            this.__eventsOverlapCheck(action, data); // events' overlap not allowed.
                        }
                        if (action == "update") {
                            this.events.forEach((e, i) => {
                                if (e.id == data.id) {
                                    this.events[i] = data;
                                    this.__eventsOverlapCheck(action, data);
                                }
                            });
                        }
                        if (action == "delete") {
                            this.events.forEach((e, i) => {
                                if (e.id == data.id) {
                                    delete this.events[i];
                                }
                            });
                        }
                        
                        await this.__persist(action, data);
                    }
                    catch({name, message}) {
                        if (message) { 
                            alert(message); 
                        }

                        this.events = await this.__listEvents(this.selectedGroupId); // reload saved events.
                    }
                }
                else {
                    this.events = [];
                }
            },

            // **************************************************************************************************************************************************
            // Private
            // **************************************************************************************************************************************************            

            async __listGroups() {
                try {
                    let groups = await this.get(this.backendUrl + "groups/");
                    return groups.data.items;
                }
                catch({name, message}) {
                    notification.open({
                        description: message
                    });
                }
            },

            async __listEvents(groupId) {
                try {
                    const events = await this.get(this.backendUrl + "events/?group_id=" + groupId + "&loadPlaylist=true");
                    return events.data.items;
                }
                catch({name, message}) {
                    alert(message);
                }  
            },

            __eventsOverlapCheck(action, data) {                  
                if (action == "create" || action == "update") {
                    this.events.forEach((e, i) => {
                        if (e.id != data.id) {
                            if (this.toUnixTimestamp(e.end_date) <= this.toUnixTimestamp(data.start_date) || this.toUnixTimestamp(e.start_date) >= this.toUnixTimestamp(data.end_date)) {
                                ;
                            }
                            else {
                                notification.open({
                                    description: "Events' overlap is not allowed."
                                });

                                throw new Error();
                            }
                        }
                    });
                }
            },

            async __persist(action, data) {
                if (action == "create") {
                    try {
                        // Create event.
                        await this.post(this.backendUrl + "events/",  {
                            data: {
                                id: data.id,
                                start_date: data.start_date,
                                end_date: data.end_date,
                                text: data.text
                            }
                        });

                        // Link event to group.
                        await this.post(this.backendUrl + "event/" + data.id + "/groups/",  {
                            data: {
                                group: {
                                    id: this.selectedGroupId
                                }
                            }
                        });                        
                    }
                    catch({name, message}) {
                        notification.open({
                            description: message
                        });

                        this.loadEvents(this.selectedGroupId); // refetch remote datastore.
                    }
                }

                if (action == "update") {
                    try {
                        await this.patch(this.backendUrl + "event/" + data.id + "/",  {
                            data: {
                                start_date: data.start_date,
                                end_date: data.end_date,
                                text: data.text
                            }
                        });

                        // Link event to playlist.
                        if (data.playlist && parseInt(data.playlist) > 0) {
                            await this.post(this.backendUrl + "event/" + data.id + "/playlists/",  {
                                data: {
                                    playlist: {
                                        id: data.playlist
                                    }
                                }
                            });
                        }
                        else {
                            await this.delete(this.backendUrl + "event/" + data.id + "/playlist/0/");
                        }          
                    }
                    catch({name, message}) {
                        notification.open({
                            description: message
                        });

                        this.loadEvents(this.selectedGroupId); // refetch remote datastore.
                    } 
                }

                if (action == "delete") {
                    try {
                        await this.delete(this.backendUrl + "event/" + data.id + "/");
                    }
                    catch({name, message}) {
                        notification.open({
                            description: message
                        });

                        this.loadEvents(this.selectedGroupId); // refetch remote datastore.
                    } 
                } 
            }
        },
    };
</script>

<template>
    <a-select
        :options="groups"
        :fieldNames="{ 
            value: 'id', 
            label: 'name' 
        }"
        placeholder="Select a group of players..."
        autofocus
        @change="loadEvents"
        style="width: 400px; position:relative; top: -12px; left:-12px;">
    </a-select>

    <Scheduler class="scheduler-container" :events="events" @event-updated="eventsUpdate"></Scheduler>
</template>

<style>
    .scheduler-container {
        overflow: hidden;
        height: 80vh;
        width: 100%;
    }
</style>
