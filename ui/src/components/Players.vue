<script>    
    import { notification } from 'ant-design-vue';
    import { ReloadOutlined } from "@ant-design/icons-vue";

    import ApiSupplicant from "../helpers/ApiSupplicant.vue"

    export default {
        components: { ReloadOutlined },
        mixins: [
            ApiSupplicant
        ],
        data() {
            return {
                players: [],
                groups: [],
                columns: [
                    { title: 'UUID', dataIndex: 'uuid', key: 'uuid' },
                    { title: 'Type', dataIndex: 'player_type', key: 'player_type', sorter: (a, b) => a.typlayer_typepe >= b.player_type, sortDirections: ['ascend'], width: 100 },
                    { title: 'Name', dataIndex: 'name', key: 'name', sorter: (a, b) => a.name >= b.name, defaultSortOrder: 'ascend', sortDirections: ['ascend'] },
                    { title: 'Address', dataIndex: 'address', key: 'address' },
                    { title: 'Position', dataIndex: 'position', key: 'position' },
                    { title: 'Comment', dataIndex: 'comment', key: 'comment' },
                    { title: 'Metrics', dataIndex: 'metrics', key: 'metrics' },
                    { title: 'Group', dataIndex: 'groupName', key: 'groupName' }
                ],
                selectedPlayerIds: [],
                rowSelection: {
                    onChange: (selectedRowKeys) => {
                        this.selectedPlayerIds = selectedRowKeys;
                    }
                }
            };
        },
        async created () {
            await this.list();           
            await this.listGroups();
        },
        mounted() {
            ;
        },
        methods: {
            // **************************************************************************************************************************************************
            // Public
            // **************************************************************************************************************************************************

            async list() {
                this.players = await this.__list(); 
            },

            async listGroups() {
                this.groups = await this.__listGroups();     
            },

            addToGroup(e) {
                const groupId = e.key;
                const groupName = e.item.name;

                if (this.selectedPlayerIds.length > 0) {
                    if (confirm("Add selected players to " + groupName + "?")) {
                        this.selectedPlayerIds.forEach(playerId => {
                            this.players = this.players.map(function(p) {
                                if (p.id == playerId) {
                                    p.groupName = groupName;
                                    p.group = {
                                        id: groupId,
                                        name: groupName
                                    }

                                    // Remote datastore.
                                    this.__doGroup(groupId, p.id);
                                }

                                return p;
                            }, this);
                        });
                    }
                }
            },

            removeFromGroup() {
                if (this.selectedPlayerIds.length > 0) {
                    if (confirm("Remove selected players from their group/s?")) {
                        this.selectedPlayerIds.forEach(playerId => {
                            this.players = this.players.map(function(p) {
                                if (p.group) {
                                    const originalGroupId = p.group.id;
                                    if (p.id == playerId) {
                                        p.groupName = "";
                                        p.group = {
                                            id: 0,
                                            name: ""
                                        }

                                        if (originalGroupId) {
                                            this.__doUngroup(originalGroupId, p.id); // remote datastore.
                                        }
                                    }
                                }

                                return p;
                            }, this);
                        });
                    }
                }
            },

            // **************************************************************************************************************************************************
            // Private
            // **************************************************************************************************************************************************

            async __list() {
                try {
                    let players = await this.get(this.backendUrl + "players/?loadGroup=true");
                    players = players.data.items;
                    players.forEach((p, i) => {
                        players[i].key = p.id; // key "key" is needed by Ant table.
                        if (p.group) {
                            players[i].groupName = p.group.name; // additional column.
                        }
                    });
                    return players;
                }
                catch({name, message}) {
                    alert(message);
                }  
            },

            async __listGroups() {
                try {
                    let groups = await this.get(this.backendUrl + "groups/");
                    groups = groups.data.items;
                    groups.forEach((g, i) => {
                        groups[i].key = g.id; // key "key" is needed by Ant table.
                    });
                    return groups;
                }
                catch({name, message}) {
                    alert(message);
                }  
            },

            async __doGroup(groupId, playerId) {
                try {
                    await this.post(
                        this.backendUrl + "group/" + groupId + "/players/",  {
                            data: {
                                player: {
                                    id: playerId
                                }
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

            async __doUngroup(groupId, playerId) {
                try {
                    await this.delete(this.backendUrl + "group/" + groupId + "/player/" + playerId + "/");
                }
                catch({name, message}) {
                    notification.open({
                        description: message
                    });

                    this.list(); // refetch remote datastore.
                }
            }
        },
    };
</script>

<template>
    <a-table 
        :columns="columns" 
        :data-source="players"  
        :pagination="{ pageSize: 20 }"
        :scroll="{ y: '60vh' }"
        :row-selection="rowSelection"
        bordered>
    </a-table>

    <a-space wrap>
        <!-- Reload players -->
        <a-button @click="list"><template #icon><ReloadOutlined /></template></a-button>

        <!-- Player/s add to group -->
        <a-dropdown>
            <template #overlay>
                <a-menu @click="addToGroup">
                    <li v-for="g in groups">
                        <a-menu-item :key="g.id" :name="g.name">{{ g.name }}</a-menu-item>                        
                    </li>
                </a-menu>
            </template>
            <a-button type="primary">
                Add to group
            </a-button>
        </a-dropdown>

        <!-- Player/s remove from group -->
        <a-button type="primary" @click="removeFromGroup">Ungroup</a-button>
    </a-space>
</template>
