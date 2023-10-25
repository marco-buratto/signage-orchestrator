<script>
    import { GroupOutlined, AppstoreOutlined, PlaySquareOutlined, FieldTimeOutlined } from "@ant-design/icons-vue";

    import Groups from "./components/Groups.vue"
    import Players from "./components/Players.vue"
    import WebPlaylists from "./components/WebPlaylists.vue"
    import SlideshowPlaylists from "./components/SlideshowPlaylists.vue"
    import SchedulerInterface from "./components/SchedulerInterface.vue"

    export default {
        components: { GroupOutlined, AppstoreOutlined, PlaySquareOutlined, FieldTimeOutlined, Groups, SchedulerInterface, Players, WebPlaylists, SlideshowPlaylists },
        data() {
            return {
                selectedKeys: ["5"],
                selectedView: "5"
            };
        },
        watch: {
            selectedKeys(n, o) {
                if (n[0] != 6)
                    this.selectedView = n[0];
            }
        },
    };
</script>

<template>
    <a-layout :style="{height:'100vh'}">
        <a-layout-header :style="{ position: 'fixed', zIndex: 10, width: '100%', height: '36px' }">
            <div class="logo" />
            <a-menu
                v-model:selectedKeys="selectedKeys"
                theme="dark"
                mode="horizontal"
                :style="{ height: '36px', lineHeight: '36px' }"
            >
                <a-menu-item key="1"><GroupOutlined/> Groups</a-menu-item>
                <a-menu-item key="2"><AppstoreOutlined/> Players</a-menu-item>
                <a-menu-item key="3"><PlaySquareOutlined/> Web Signage Playlists</a-menu-item>
                <a-menu-item key="4"><PlaySquareOutlined/> Slideshow Playlists</a-menu-item>
                <a-menu-item key="5"><FieldTimeOutlined/> Events</a-menu-item>

                <a-menu-item key="6">
                    <a-tooltip placement="bottom">
                        <template #title>
                            <div>
                                All available players (Pis running Raspberry Digital Signage or Slideshow) are enlisted in the Players table, if configured to use the Orchestrator.<br>
                                You can add each player to a Group. Playlists are player configurations. In the Events tab you can schedule a group of players to use a playlist.
                            </div>
                        </template>
                        [ ? ]
                    </a-tooltip>
                </a-menu-item>
            </a-menu>
        </a-layout-header>
        <a-layout-content :style="{ padding: '0 50px', marginTop: '36px' }">
            <div :style="{ background: '#fff', padding: '24px', minHeight: '380px' }">
                <div v-if="selectedView == '1'">
                    <Groups></Groups>       
                </div>
                <div v-if="selectedView == '2'">
                    <Players></Players>
                </div>
                <div v-if="selectedView == '3'">
                    <WebPlaylists></WebPlaylists>
                </div>
                <div v-if="selectedView == '4'">
                    <SlideshowPlaylists></SlideshowPlaylists>
                </div>         
                <div v-if="selectedView == '5'">
                    <SchedulerInterface></SchedulerInterface>
                </div>
            </div>
        </a-layout-content>
        <a-layout-footer :style="{ textAlign: 'center' }">
            Signage Orchestrator by <a href="https://www.binaryemotions.com" target="_blank">Binary Emotions</a>
        </a-layout-footer>
    </a-layout>
</template>
