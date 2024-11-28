<template>
	<div class="wrapper">
		<NavigationPanel
			:navigation-buttons="panelsData"
			class="panel"
			@click="onNavButtonClicked"
			@logout="onLogout"
		></NavigationPanel>
		<ModalMessage
			v-if="errorWindowVisible"
			title="Ошибка"
			:description="errorDescription"
			@close="onErrorClosed"
		>
		</ModalMessage>

		<component
			v-for="panelData in panelsData"
			class="panel-content"
			:is="panelData.panel"
			:id="panelID"
			@notify="(count: number, _: number) => (panelData.notifyCount = count)"
			v-show="panelData.isActive"
		></component>
		<component
			class="panel-content"
			:is="panel"
			v-if="panelsData.length === 0"
		></component>
	</div>
</template>
<script setup lang="ts">
import NavigationPanel from "@/components/NavigationPanel.vue";
import DefaultPanel from "@/pages/panels/DefaultPanel.vue";
import { getPanelsByAccesses } from "@/pages/panels";
import { useNetworkStore } from "@/store/network";
import { ref, shallowRef, watch } from "vue";
import ModalMessage from "@/components/ModalMessage.vue";

const networkStore = useNetworkStore();

const panelsData = ref(getPanelsByAccesses(networkStore.accesses));

const panel = shallowRef(DefaultPanel);
let panelID = 0;
if (panelsData.value.length > 0) {
	panelsData.value[0].isActive = true;
	panelID = panelsData.value[0].id;
}

const onNavButtonClicked = async (id: number) => {
	const activePanelData = panelsData.value.find(
		(panelData) => panelData.isActive,
	);

	const panelData = panelsData.value.find((panelData) => panelData.id === id);
	if (!panelData) return;

	if (activePanelData) activePanelData.isActive = false;

	panelID = panelData.id;
	panelData.isActive = true;
};

const onLogout = () => {
	networkStore.logout();
};

const errorWindowVisible = ref(false);
const errorDescription = ref("");
const onErrorClosed = () => {
	errorWindowVisible.value = false;
	networkStore.errors.pop();
};
watch(networkStore.errors, () => {
	if (networkStore.errors.length === 0) {
		return;
	}
	errorDescription.value = networkStore.errors[networkStore.errors.length - 1];
	errorWindowVisible.value = true;
});
</script>
<style scoped>
.wrapper {
	display: flex;
	flex-direction: row;
	height: 100%;
	gap: 40px;
	background-color: #f6f6f6;
	width: 100%;
}

.panel-content {
	min-width: 0;
	flex-grow: 1;
}
.panel {
	flex-grow: 0;
	flex-shrink: 0;
	max-height: 100%;
	min-height: 0;
}
</style>
