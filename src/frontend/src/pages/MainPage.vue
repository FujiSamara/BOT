<template>
    <div class="wrapper">
        <NavigationPanel
        :navigation-buttons="navigationButtons"
        class="panel"
        @click="onButtonClicked"
        ></NavigationPanel>
        <PanelHandler class="panel-handler"></PanelHandler>
    </div>
</template>
<script setup lang="ts">
import NavigationPanel from '@/components/NavigationPanel.vue'
import PanelHandler from '@/components/PanelHandler.vue'
import { NavigationButton } from '@/types';

const navigationButtons: Array<NavigationButton> = [
    {
        id: 1,
        imageSrc: "/img/bid_logo.svg",
        label: "Заявки",
        isActive: false
    },
    {
        id: 2,
        imageSrc: "/img/bid_logo.svg",
        label: "Заявки",
        isActive: true
    }
]

const onButtonClicked = async (id: number) => {
    console.log(id)
}
</script>
<style scoped>
.wrapper {
    display: flex;
    width: 100%;
    height: 100%;
    gap: 40px;
    background-color: #F6F6F6;
}

.panel-handler {
    border: 1px solid black;
    width: 100%;
    height: 100%;
}
</style>