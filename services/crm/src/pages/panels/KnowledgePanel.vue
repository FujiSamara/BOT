<script setup lang="ts">
import { computed, onMounted, ref, useId, watch } from "vue";
import { useRoute, useRouter } from "vue-router";

import MaybeDelayInput from "@/components/MaybeDelayInput.vue";

import { DivisionType, KnowledgeController } from "@/components/knowledge";
import Division from "@/components/knowledge/Division.vue";
import Card from "@/components/knowledge/Card.vue";

const router = useRouter();
const route = useRoute();
const controller = new KnowledgeController();

const division = computed(() => {
	if (controller.division === undefined) return undefined;

	return controller.division.value;
});
const card = computed(() => {
	if (controller.card === undefined) return undefined;

	return controller.card.value;
});

const searchValue = ref("");
const onSearch = async (val: string) => {
	searchValue.value = val;
	const query = { ...route.query };
	if (val.length === 0) delete query["term"];
	else query["term"] = val;
	await router.push({ name: "knowledge-search", query: query });
};

const loadDivision = async () => {
	await router.isReady();

	if (route.name === "knowledge-search") {
		const term = route.query["term"] as string;

		if (term === undefined) await router.push("main");

		if (term.length > 2) await controller.searchDivisions(term);
		return;
	}

	const path = route.path
		.split("knowledge")[1]
		.split("/")
		.filter((v) => v);
	await controller.loadDivision("/" + path.join("/"));
};

const subDivisionClicked = async (index: number) => {
	if (division.value === undefined) return;

	const path =
		route.path.split("knowledge")[0] +
		"knowledge" +
		division.value.subdivisions[index].path;
	await router.push({ path: path });
};

watch(route, loadDivision);
onMounted(async () => {
	await loadDivision();
});
</script>
<template>
	<div class="knowledge-panel">
		<MaybeDelayInput
			class="search"
			placeholder="Поиск"
			:value="searchValue"
			@submit="onSearch"
			:id="useId()"
		></MaybeDelayInput>

		<div class="wrapper" v-if="division !== undefined">
			<Transition name="fade" mode="out-in">
				<Division
					:key="division.id"
					v-if="division.type == DivisionType.division"
					:division="division"
					@click="subDivisionClicked"
				></Division>
				<Card v-else-if="card" :card="card" :path="division.path"></Card>
			</Transition>
		</div>
	</div>
</template>
<style scoped lang="scss">
.knowledge-panel {
	display: flex;
	flex-direction: column;

	gap: 24px;

	width: 100%;
	height: 100%;

	.search {
		width: 100%;
		height: 48px;

		border-color: $stroke-light-blue;
	}
}
</style>
