<script>
    import { scheduler } from "dhtmlx-scheduler";

    import ApiSupplicant from "../helpers/ApiSupplicant.vue"    

    export default {
        mixins: [
            ApiSupplicant
        ],        
        data() {
            return {
                playlists: []
            };
        },        
        props: {
            events: {
                default() {
                    return [];
                },
            }              
        },
        created() {
            this.$_initDataProcessor();
            scheduler.clearAll();
        },
        async mounted() {
            await this.listPlaylists();

            scheduler.skin = "material";
            scheduler.config.header = ["day", "week", "month", "date", "prev", "today", "next"];

            scheduler.plugins({
                //collision: true,
                all_timed: true
            });

            // https://docs.dhtmlx.com/scheduler/lightbox_editors_manipulations.html
            // https://docs.dhtmlx.com/scheduler/event_object_operations.html            
            scheduler.config.lightbox.sections=[
                { name:"description", height:50, type:"textarea", map_to:"text", focus:true },
                { name:"Playlist", map_to:"playlist", type:"select", options:scheduler.serverList("options", this.playlists), focus:true },
                { name:"time", height:72, type:"time", map_to:"auto" }
            ];            

            scheduler.config.show_loading = true;
            scheduler.config.container_autoresize = true;
            scheduler.config.all_timed = true;
            scheduler.config.full_day = true;
            scheduler.init(
                this.$refs.SchedulerComponent,
                new Date(),
                "week"
            );
        },
        updated() {
            console.log("Scheduler updating...");
            this.events.forEach((p, i) => {
                if (p.playlist) {
                    this.events[i].playlist = p.playlist.id; // flatten received data structure.
                }
            });

            scheduler.clearAll();
            scheduler.parse(this.events);
        },

        methods: {
            // **************************************************************************************************************************************************
            // Public
            // **************************************************************************************************************************************************

            async listPlaylists() {
                try {
                    this.playlists = await this.get(this.backendUrl + "playlists/");
                    this.playlists = [{"id": 0, "name": "--"}].concat(this.playlists.data.items);
                    this.playlists.forEach((p, i) => {
                        // Add additional lightbox needed keys.
                        this.playlists[i].key = p.id;
                        this.playlists[i].label = p.name;
                    });
                }
                catch({name, message}) {
                    alert(message);
                }                
            },

            // **************************************************************************************************************************************************
            // Private
            // **************************************************************************************************************************************************               

            $_initDataProcessor() {
                scheduler.createDataProcessor((entity, action, data, id) => { 
                    this.$emit(`${entity}-updated`, action, data);
                });
            }           
        }
    };
</script>

<template>
    <div ref="SchedulerComponent"></div>
</template>

<style>
    @import "dhtmlx-scheduler/codebase/dhtmlxscheduler_material.css";
</style>