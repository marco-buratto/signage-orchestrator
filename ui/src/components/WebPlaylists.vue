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
                    { title: 'Name', dataIndex: 'name', key: 'name', defaultSortOrder: 'ascend', sortDirections: ['ascend'], width: 120 },
                    { title: 'URL', dataIndex: 'url', key: 'url', width: '100%' },
                    { title: 'Compatibility', dataIndex: 'compatibility', key: 'compatibility', width: 140 },
                    { title: 'Pointer disabled', dataIndex: 'pointer_disabled', key: 'pointer_disabled', width: 140 },
                    { title: 'Reset time', dataIndex: 'reset_time_min', key: 'reset_time_min', width: 120 },
                    { title: 'Reload time', dataIndex: 'reload_time_s', key: 'reload_time_s', width: 120 },
                    { title: '', dataIndex: 'operation', width: 90 }
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
                currentPlaylist: {},
                currentPlaylistError: {},
                currentPlaylistDisabled: {},
            };
        },
        async created () {
            await this.list();
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

            setModal(data) {
                if (data) {                    
                    this.currentPlaylist = {
                        id: data.id,
                        key: data.key,
                        name: data.name,
                        rds: {
                            url: data.url,
                            compatibility: data.compatibility,
                            pointer_disabled: data.pointer_disabled,
                            reset_time_min: data.reset_time_min,
                            reload_time_s: data.reload_time_s
                        }
                    }
                }
                else {
                    this.currentPlaylist = { 
                        id: 0,
                        key: 0,
                        name: "",
                        rds: {
                            url: "",
                            compatibility: "no",
                            pointer_disabled: "no",
                            reset_time_min: 0,
                            reload_time_s: 0
                        }
                    }
                }

                this.currentPlaylistError = {
                    name: "",
                    url: "",
                    reset_time_min: "",
                    reload_time_s: ""
                }

                this.currentPlaylistDisabled.reload_time_s = false;
                if (this.currentPlaylist.rds.compatibility == "no") {
                    this.currentPlaylistDisabled.reload_time_s = true;
                }
            },

            modalCompatibilityModeChange(v) {
                this.currentPlaylistDisabled.reload_time_s = false;
                if (v == "no") {
                    this.currentPlaylistDisabled.reload_time_s = true;
                    this.currentPlaylist.rds.reload_time_s = 0;
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
                ["url", "reset_time_min", "reload_time_s"].forEach(e => {                    
                    if (pl.rds[e] === "") {
                        this.currentPlaylistError[e] = "error";
                        error = true;
                    }
                });

                if (!error) {
                    if (!pl.id) {
                        // Addition.
                        this.__add(pl.name, pl.rds.url, pl.rds.compatibility, pl.rds.pointer_disabled, pl.rds.reset_time_min, pl.rds.reload_time_s); // remote datastore (mediaconf in base64).
                    }
                    else {
                        // Modification.
                        this.playlists = this.playlists.map(function(p) {
                            if (p.id == pl.id) {
                                p = {
                                    id: pl.id,
                                    key: pl.key,                                      
                                    name: pl.name,
                                    url: pl.rds.url,
                                    compatibility: pl.rds.compatibility,
                                    pointer_disabled: pl.rds.pointer_disabled,
                                    reset_time_min: pl.rds.reset_time_min,
                                    reload_time_s: pl.rds.reload_time_s
                                }

                                this.__modify(pl.id, pl.name, pl.rds.url, pl.rds.compatibility, pl.rds.pointer_disabled, pl.rds.reset_time_min, pl.rds.reload_time_s); // remote datastore (mediaconf in base64).
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

            async __list() {
                try {
                    let playlists = await this.get(this.backendUrl + "playlists/?filter=web");
                    playlists = playlists.data.items;
                    playlists.forEach((p, i) => {
                        playlists[i].key = p.id; // key "key" is needed by Ant table.
                        ["compatibility", "pointer_disabled"].forEach(e => {
                            if (playlists[i][e]) 
                                playlists[i][e] = "yes"
                            else playlists[i][e] = "no"
                        });
                    });
                    return playlists;
                }
                catch({name, message}) {
                    alert(message);
                }  
            },

            async __add(name, url, compatibility, pointer_disabled, reset_time_min, reload_time_s) {
                try {
                    await this.post(
                        this.backendUrl + "playlists/",  {
                            data: {
                                playlist_type: "web",
                                name: name,
                                url: url,
                                compatibility: compatibility,
                                pointer_disabled: pointer_disabled,
                                reset_time_min: reset_time_min,
                                reload_time_s: reload_time_s
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

            async __modify(id, name, url, compatibility, pointer_disabled, reset_time_min, reload_time_s) {
                try {
                    await this.patch(
                        this.backendUrl + "playlist/" + id + "/",  {
                            data: {
                                playlist_type: "web",
                                name: name,
                                url: url,
                                compatibility: compatibility,
                                pointer_disabled: pointer_disabled,
                                reset_time_min: reset_time_min,
                                reload_time_s: reload_time_s
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
            <template v-if="column.dataIndex === 'operation'">
                <div class="editable-row-operations">
                    <a @click="edit(record.key)"><EditOutlined /> Edit</a>
                </div>
            </template>              
        </template>
    </a-table>

    <a-modal v-model:open="openModal" title="Playlist" @ok="persist" width="650px">
        <br />Name:<br/><a-input v-model:value="currentPlaylist.name" :status="currentPlaylistError.name" @change="currentPlaylistError.name=''"></a-input><br /><br />
        URL:<br/><a-input v-model:value="currentPlaylist.rds.url" :status="currentPlaylistError.url" @change="currentPlaylistError.url=''"></a-input><br /><br />

        Compatibility mode:<br/> 
        <a-select v-model:value="currentPlaylist.rds.compatibility" @change="modalCompatibilityModeChange" style="width: 602px">
            <a-select-option value="no">no</a-select-option>
            <a-select-option value="yes">yes</a-select-option>
        </a-select><br /><br />

        Pointer disabled:<br/> 
        <a-select v-model:value="currentPlaylist.rds.pointer_disabled" style="width: 602px">
            <a-select-option value="no">no</a-select-option>
            <a-select-option value="yes">yes</a-select-option>
        </a-select><br /><br />        
        
        Reset time (min):<br/> <a-input v-model:value="currentPlaylist.rds.reset_time_min" :status="currentPlaylistError.reset_time_min" @change="currentPlaylistError.reset_time_min=''"></a-input><br /><br />
        Reload time (s):<br/> <a-input v-model:value="currentPlaylist.rds.reload_time_s" :disabled="currentPlaylistDisabled.reload_time_s" :status="currentPlaylistError.reload_time_s" @change="currentPlaylistError.reload_time_s=''"></a-input><br /><br />
    </a-modal>

    <a-space wrap>
        <!-- Playlist add -->
        <a-button type="primary" @click="setModal(); openModal=true">Add</a-button>

        <!-- Playlist delete -->
        <a-button type="primary" danger @click="remove">Delete</a-button>
    </a-space>
</template>
