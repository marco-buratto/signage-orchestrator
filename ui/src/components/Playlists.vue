<script>    
    import { notification } from 'ant-design-vue';
    import { EditOutlined } from "@ant-design/icons-vue";
    import { cloneDeep } from 'lodash-es';

    import ApiSupplicant from "../helpers/ApiSupplicant.vue"

    export default {
        components: { EditOutlined },
        mixins: [
            ApiSupplicant
        ],
        data() {
            return {
                playlists: [],
                columns: [
                    { title: 'Name', dataIndex: 'name', key: 'name', defaultSortOrder: 'ascend', sortDirections: ['ascend'], width: '25%' },
                    { title: 'media.conf', dataIndex: 'mediaconf', key: 'mediaconf', width: '75%' },
                    { title: 'Transition time (s)', dataIndex: 'transition', key: 'transition', width: 160 },
                    { title: 'Blend time (ms)', dataIndex: 'blend', key: 'blend', width: 160 },
                    { title: '', dataIndex: 'operation', width: 120 }
                ],
                selectedPlaylistsIds: [],
                rowSelection: {
                    onChange: (selectedRowKeys) => {
                        this.selectedPlaylistsIds = selectedRowKeys;
                    }
                },
                edit: key => {
                    this.openModal = true;
                    this.setModal(
                        cloneDeep(this.playlists.filter(item => key === item.key)[0])
                    );
                },       
                openModal: false,
                rsDefaultMediaconf: "",
                currentPlaylist: {},
                currentPlaylistError: {}
            };
        },
        async created () {
            await this.list();
            await this.getRsDefaultMediaconf();
        },        
        mounted() {
            ;
        },
        methods: {
            // **************************************************************************************************************************************************
            // Public
            // **************************************************************************************************************************************************

            async list() {
                this.playlists = await this.__list();
            },

            async getRsDefaultMediaconf() {
                this.rsDefaultMediaconf = await this.__rsDefaultMediaconf();
            },            

            setModal(data) {
                if (data) {                    
                    this.currentPlaylist = {
                        id: data.id,
                        key: data.key,
                        name: data.name,
                        rs: {
                            mediaconf: data.mediaconf,
                            transition: data.transition,
                            blend: data.blend
                        }
                    }
                    this.currentPlaylistError = {
                        name: "",
                        mediaconf: "",
                        transition: "",
                        blend: ""
                    }     
                }
                else {
                    this.currentPlaylist = { 
                        id: 0,
                        key: 0,
                        name: "",
                        rs: {
                            mediaconf: this.rsDefaultMediaconf,
                            transition: 10,
                            blend: 600
                        }
                    }
                    this.currentPlaylistError = {
                        name: "",
                        mediaconf: "",
                        transition: "",
                        blend: ""
                    }
                }
            },

            persist() {
                let error = false;
                const pl = this.currentPlaylist;

                // Error checks.
                if (!pl.name) {
                    error = true;
                    this.currentPlaylistError.name = "error";
                }
                ["mediaconf", "transition", "blend"].forEach(e => {
                    if (!pl.rs[e]) {
                        this.currentPlaylistError[e] = "error";
                        error = true;
                    }
                });

                if (!error) {
                    if (!pl.id) {
                        // Addition.
                        this.__add(pl.name, btoa(pl.rs.mediaconf), pl.rs.transition, pl.rs.blend); // remote datastore (mediaconf in base64).
                    }
                    else {
                        // Modification.
                        this.playlists = this.playlists.map(function(p) {
                            if (p.id == pl.id) {
                                p = {
                                    id: pl.id,
                                    key: pl.key,                                      
                                    name: pl.name,
                                    mediaconf: pl.rs.mediaconf,
                                    transition: pl.rs.transition,
                                    blend: pl.rs.blend
                                }

                                this.__modify(pl.id, pl.name, btoa(pl.rs.mediaconf), pl.rs.transition, pl.rs.blend); // remote datastore (mediaconf in base64).
                            }

                            return p;
                        }, this);
                    }

                    this.openModal = false;
                    this.setModal();
                }
            },

            remove() {
                if (this.selectedPlaylistsIds.length > 0) {
                    if (confirm("Delete selected playlists?")) {
                        this.selectedPlaylistsIds.forEach((s) => {
                            this.playlists.forEach((p, i) => {
                                if (p.id == s) {
                                    delete this.playlists[i]; // memory.
                                    this.__delete(p.id); // remote datastore.
                                }
                            });
                        });
                    }
                }
            },

            // **************************************************************************************************************************************************
            // Private
            // **************************************************************************************************************************************************
            
            async __rsDefaultMediaconf() {
                try {
                    return await this.get("/raspberry-player/slideshow/media.conf");
                }
                catch({name, message}) {
                    alert(message);
                }  
            },            

            async __list() {
                try {
                    let playlists = await this.get(this.backendUrl + "playlists/?filter=slideshow");
                    playlists = playlists.data.items;
                    playlists.forEach((p, i) => {
                        playlists[i].key = p.id; // key "key" is needed by Ant table.
                        playlists[i].mediaconf = atob(p.mediaconf); // base64 decode.
                    });
                    return playlists;
                }
                catch({name, message}) {
                    alert(message);
                }  
            },

            async __add(name, mediaconf, transition, blend) {
                try {
                    await this.post(
                        this.backendUrl + "playlists/",  {
                            data: {
                                playlist_type: "slideshow",
                                name: name,
                                mediaconf: mediaconf,
                                transition: transition,
                                blend: blend
                            }
                        }
                    );
                }
                catch({name, message}) {
                    notification.open({
                        description: message
                    });
                }
                finally {
                    this.list(); // refetch remote datastore.
                }                
            },
            
            async __modify(id, name, mediaconf, transition, blend) {
                try {
                    await this.patch(
                        this.backendUrl + "playlist/" + id + "/",  {
                            data: {
                                playlist_type: "slideshow",
                                name: name,
                                mediaconf: mediaconf,
                                transition: transition,
                                blend: blend
                            }
                        }
                    );
                }
                catch({name, message}) {
                    notification.open({
                        description: message
                    });

                    this.list(); // refetch remote datastore.
                }  
            },            

            async __delete(id) {
                try {
                    await this.delete(this.backendUrl + "playlist/" + id + "/");
                }
                catch({name, message}) {
                    notification.open({
                        description: message
                    });

                    this.list(); // refetch remote datastore.
                }  
            },
        },
    };
</script>

<template>
    <a-table 
        :columns="columns" 
        :data-source="playlists"  
        :pagination="{ pageSize: 20 }"
        :scroll="{ y: '60vh' }"
        :row-selection="rowSelection"
        bordered>

        <template #bodyCell="{ column, text, record }">
            <template v-if="column.key === 'mediaconf'">
                <a-textarea :value="text" :auto-size="{ minRows: 3, maxRows: 18 }"/>
            </template>            
            <template v-if="column.dataIndex === 'operation'">
                <div class="editable-row-operations">
                    <a @click="edit(record.key)"><EditOutlined /> Edit</a>
                </div>
            </template>              
        </template>
    </a-table>

    <a-modal v-model:open="openModal" title="Playlist" @ok="persist" width="650px">
        <br />Name:<br/><a-input v-model:value="currentPlaylist.name" :status="currentPlaylistError.name" @change="currentPlaylistError.name=''"></a-input><br /><br />
        media.conf:<br/> <a-textarea v-model:value="currentPlaylist.rs.mediaconf" :auto-size="{ minRows: 3, maxRows: 8 }" :status="currentPlaylistError.mediaconf" @change="currentPlaylistError.mediaconf=''"></a-textarea><br /><br />
        Transition time (s):<br/> <a-input v-model:value="currentPlaylist.rs.transition" :status="currentPlaylistError.transition" @change="currentPlaylistError.transition=''"></a-input><br /><br />
        Blend time (ms):<br/> <a-input v-model:value="currentPlaylist.rs.blend" :status="currentPlaylistError.blend" @change="currentPlaylistError.blend=''"></a-input><br /><br />
    </a-modal>

    <a-space wrap>
        <!-- Playlist add -->
        <a-button type="primary" @click="setModal(); openModal=true">Add</a-button>

        <!-- Playlist delete -->
        <a-button type="primary" danger @click="remove">Delete</a-button>
    </a-space>
</template>
