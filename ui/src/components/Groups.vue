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
                groups: [],
                columns: [
                    { title: 'Name', dataIndex: 'name', key: 'name', defaultSortOrder: 'ascend', sortDirections: ['ascend'] },
                    { title: 'Comment', dataIndex: 'comment', key: 'comment' },
                    { title: '', dataIndex: 'operation', width: 120 }
                ],
                selectedGroupIds: [],
                rowSelection: {
                    onChange: (selectedRowKeys) => {
                        this.selectedGroupIds = selectedRowKeys;
                    }
                },                
                editableData: {},
                edit: key => {
                    this.editableData[key] = cloneDeep(this.groups.filter(item => key === item.key)[0]);
                },
                openModal: false,
                newGroup: {},
                newGroupNameError: ""
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
                this.groups = await this.__list();
            },

            resetModal() {
                this.newGroup = { 
                    name: "",
                    comment: ""
                }
            },            

            add() {
                const g = this.newGroup;
                if (g.name) {
                    this.__add(g.name, g.comment); // remote datastore.

                    this.openModal = false;
                    this.resetModal();                    
                }
                else {
                    this.newGroupNameError = "error";
                }
            },

            modify(key) {
                if (this.editableData[key].name) {
                    Object.assign(this.groups.filter(item => key === item.key)[0], this.editableData[key]); // memory.
                    this.__modify(key, this.editableData[key]); // remote datastore.

                    delete this.editableData[key];
                }
                else {
                    notification.open({
                        description: "Group name must be set"
                    });
                }
            },

            remove() {
                const selectedGroupIds = this.selectedGroupIds;
                if (selectedGroupIds.length > 0) {
                    if (confirm("Delete selected groups?")) {
                        selectedGroupIds.forEach((s) => {
                            this.groups.forEach((g, i) => {
                                if (g.id == s) {
                                    delete this.groups[i]; // memory.
                                    this.__delete(g.id); // remote datastore.
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

            async __add(name, comment) {
                try {
                    await this.post(
                        this.backendUrl + "groups/", { 
                            data: {
                                name: name,
                                comment: comment
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
            
            async __modify(id, data) {
                try {
                    await this.patch(
                        this.backendUrl + "group/" + id + "/",  {
                            data: {
                                name: data.name,
                                comment: data.comment
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
                    await this.delete(this.backendUrl + "group/" + id + "/");
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
        :data-source="groups"  
        :pagination="{ pageSize: 20 }"
        :scroll="{ y: '60vh' }"
        :row-selection="rowSelection"
        bordered>

        <template #bodyCell="{ column, text, record }">
            <template v-if="['name', 'comment'].includes(column.dataIndex)">
                <div>
                    <a-input
                        v-if="editableData[record.key]"
                        v-model:value="editableData[record.key][column.dataIndex]"
                        style="margin: -5px 0"
                    />
                    <template v-else>
                        {{ text }}
                    </template>
                </div>
            </template>
            <template v-else-if="column.dataIndex === 'operation'">
                <div class="editable-row-operations">
                    <span v-if="editableData[record.key]">
                        <a-space wrap>
                            <a-typography-link @click="modify(record.key)">Save</a-typography-link> 
                            <a @click="delete editableData[record.key]">Cancel</a>
                        </a-space>
                    </span>
                    <span v-else>
                        <a @click="edit(record.key)"><EditOutlined /> Edit</a>
                    </span>
                </div>
            </template>
        </template>
    </a-table>

    <a-modal v-model:open="openModal" title="Add new group of players" @ok="add">
        <br />
        <a-input v-model:value="newGroup.name" placeholder="Name" :status="newGroupNameError" @change="newGroupNameError=''"></a-input><br /><br />
        <a-input v-model:value="newGroup.comment" placeholder="Comment"></a-input><br /><br />
    </a-modal>

    <a-space wrap>
        <!-- Group add -->
        <a-button type="primary" @click="this.resetModal(); openModal=true">Add</a-button>

        <!-- Group delete -->
        <a-button type="primary" danger @click="remove">Delete</a-button>
    </a-space>
</template>
