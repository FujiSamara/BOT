<script setup lang="ts">
import { computed, onMounted, ref, useId } from "vue";
import { useRoute, useRouter } from "vue-router";

import MaybeDelayInput from "@/components/MaybeDelayInput.vue";

import { KnowledgeChapter, KnowledgeController } from "@/components/knowledge";
import Chapter from "@/components/knowledge/Chapter.vue";
import Card from "@/components/knowledge/Card.vue";

const router = useRouter();
const route = useRoute();
const controller = new KnowledgeController();

const chapter = computed(() => controller.division.value as KnowledgeChapter);

const searchValue = ref("");
const onSearch = async (val: string) => {
	searchValue.value = val;
};

onMounted(async () => {
	await router.isReady();

	const path = route.path
		.split("knowledge")[1]
		.split("/")
		.filter((v) => v);
	await controller.loadDivision(path);
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

		<div class="division" v-if="controller.division.value !== undefined">
			<Transition name="fade" mode="out-in">
				<Chapter
					v-if="controller.division.value.type === 'chapter'"
					:chapter="chapter"
				></Chapter>
				<Card v-else></Card>
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
