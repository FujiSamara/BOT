<template>
	<div class="wrapper">
		<NavigationPanel
		:navigation-buttons="panelsData"
		class="panel"
		@click="onNavButtonClicked"
		></NavigationPanel>
		<panel></panel>
	</div>
</template>
<script setup lang="ts">
import NavigationPanel from '@/components/NavigationPanel.vue'
import DefaultPanel from '@/panels/DefaultPanel.vue';
import { getPanelsByAccesses } from '@/panels';
import { useAuthStore } from '@/store/auth';
import { shallowRef } from 'vue';

const authStore = useAuthStore()
const panelsData = getPanelsByAccesses(authStore.accesses)
const panel = shallowRef(panelsData.length > 0? panelsData[0].panel: DefaultPanel)

const onNavButtonClicked = async (id: number) => {
	const activePanelData = panelsData.find((panelData) => panelData.isActive)

	const panelData = panelsData.find((panelData) => panelData.id === id)
	if (!panelData)
		return

	if (activePanelData)
		activePanelData.isActive = false

	panel.value = panelData.panel
	panelData.isActive = true;
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
</style>
