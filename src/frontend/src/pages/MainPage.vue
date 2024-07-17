<template>
	<div class="wrapper">
		<NavigationPanel
			:navigation-buttons="panelsData"
			class="panel"
			@click="onNavButtonClicked"
			@logout="onLogout"
		></NavigationPanel>
		<panel class="panel-content"></panel>
	</div>
</template>
<script setup lang="ts">
import NavigationPanel from "@/components/NavigationPanel.vue";
import DefaultPanel from "@/panels/DefaultPanel.vue";
import { getPanelsByAccesses } from "@/panels";
import { useAuthStore } from "@/store/auth";
import { ref, shallowRef } from "vue";

const authStore = useAuthStore();

const panelsData = ref(getPanelsByAccesses(authStore.accesses));
const panel = shallowRef(DefaultPanel);
if (panelsData.value.length > 0) {
	panel.value = panelsData.value[0].panel;
	panelsData.value[0].isActive = true;
}

const onNavButtonClicked = async (id: number) => {
	const activePanelData = panelsData.value.find(
		(panelData) => panelData.isActive,
	);

	const panelData = panelsData.value.find((panelData) => panelData.id === id);
	if (!panelData) return;

	if (activePanelData) activePanelData.isActive = false;

	panel.value = panelData.panel;
	panelData.isActive = true;
};

const onLogout = async () => {
	await authStore.logout();
};
</script>
<style scoped>
.wrapper {
	display: flex;
	flex-shrink: 1;
	flex-grow: 1;
	flex-direction: row;
	height: 100%;
	gap: 40px;
	background-color: #f6f6f6;
}

.panel-content {
	min-width: 0;
}
</style>
