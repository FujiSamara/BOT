<script setup lang="ts">
import { computed, onMounted, ref, useId, watch } from "vue";
import { useRoute, useRouter } from "vue-router";

import MaybeDelayInput from "@/components/MaybeDelayInput.vue";
import Division from "@/components/knowledge/Division.vue";
import Card from "@/components/knowledge/Card.vue";
import PulseSpinner from "@/components/UI-new/PulseSpinner.vue";

import { DivisionType, KnowledgeController } from "@/components/knowledge";

const router = useRouter();
const route = useRoute();
const controller = new KnowledgeController();
const loading = ref(false);
const extending = ref(false);

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

const subDivisionClicked = async (index: number) => {
	if (division.value === undefined) return;

	const path =
		route.path.split("knowledge")[0] +
		"knowledge" +
		division.value.subdivisions[index].path;
	await router.push({ path: path });
};
const extendClicked = async () => {
	extending.value = true;
	if (route.name === "knowledge-search") {
		const term = route.query["term"] as string;

		if (term === undefined) await router.push("main");
	}
	await controller.nextSubdivisions();
	extending.value = false;
};

const loadDivision = async () => {
	loading.value = true;
	await router.isReady();

	if (route.name === "knowledge-search") {
		const term = route.query["term"] as string;

		if (term === undefined) await router.push("main");

		if (term.length > 2) await controller.searchDivisions(term);
		loading.value = false;
		return;
	}

	const path = route.path
		.split("knowledge")[1]
		.split("/")
		.filter((v) => v);
	await controller.loadDivision("/" + path.join("/"));
	loading.value = false;
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

		<div class="content">
			<Transition name="fade" mode="out-in">
				<Division
					:key="division.id"
					v-if="!loading && division && division.type == DivisionType.division"
					:division="division"
					@click="subDivisionClicked"
					class="division"
				>
					<div class="extend-wrapper">
						<Transition name="fade" mode="out-in" :duration="250">
							<div v-if="!extending" class="next-button-wrapper">
								<button
									v-if="!controller.lastDivisionPage.value"
									@click="extendClicked"
									class="next-division"
								>
									Далее
								</button>
							</div>
							<div v-else class="pulse-wrapper">
								<PulseSpinner class="spinner"></PulseSpinner>
							</div>
						</Transition>
					</div>
				</Division>
				<Card
					v-else-if="!loading && division && card"
					:card="card"
					:path="division.path"
				></Card>
				<div v-else-if="loading" class="pulse-wrapper">
					<PulseSpinner class="spinner"></PulseSpinner>
				</div>
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

	.content {
		display: flex;
		position: relative;

		width: 100%;
		height: fit-content;

		.division {
			.extend-wrapper {
				display: flex;
				flex-direction: row;
				justify-content: center;

				width: 100%;
				height: 64px;

				.pulse-wrapper {
					.spinner {
						width: 64px;
						height: 64px;
					}
				}

				.next-button-wrapper {
					display: flex;
					flex-direction: row;
					justify-content: center;

					width: 100%;
					height: 64px;

					.next-division {
						@include field();

						width: 128px;
						justify-content: center;
					}
				}
			}
		}

		.pulse-wrapper {
			display: flex;
			justify-content: center;
			align-items: center;

			width: 100%;
			height: fit-content;

			.spinner {
				width: 128px;
				height: 128px;

				color: $main-accent-blue;
			}
		}
	}

	.fade-leave-to,
	.fade-enter-from {
		position: absolute;
	}
}
</style>
