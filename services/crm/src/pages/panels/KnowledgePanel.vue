<script setup lang="ts">
import { computed, onMounted, ref, useId, watch } from "vue";
import { useRoute, useRouter } from "vue-router";

import MaybeDelayInput from "@/components/MaybeDelayInput.vue";
import Division from "@/components/knowledge/Division.vue";
import Card from "@/components/knowledge/Card.vue";
import PulseSpinner from "@/components/UI-new/PulseSpinner.vue";

import { DivisionType } from "@/components/knowledge/types";
import { KnowledgeController } from "@/components/knowledge";

const router = useRouter();
const route = useRoute();
const controller = new KnowledgeController();
const init = ref(false);

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

const onCardSave = async (val: any) => {
	await controller.updateCard(val);
	await loadDivision();
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
	if (route.name === "knowledge-search") {
		const term = route.query["term"] as string;

		if (term === undefined) await router.push("main");

		await controller.nextSearchingResults(term);

		return;
	}
	await controller.nextSubdivisions();
};

const loadDivision = async () => {
	await router.isReady();

	if (route.name === "knowledge-search") {
		const term = route.query["term"] as string;

		if (term === undefined) await router.push("main");

		searchValue.value = term;

		if (term.length > 2) await controller.searchDivisions(term);
		return;
	}
	searchValue.value = "";

	const path = route.path
		.split("knowledge")[1]
		.split("/")
		.filter((v) => v);
	await controller.loadDivision("/" + path.join("/"));
};

watch(route, loadDivision);
onMounted(async () => {
	await loadDivision();
	init.value = true;
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
					v-if="
						!controller.divisionLoading.value &&
						division &&
						division.type == DivisionType.division
					"
					:division="division"
					@click="subDivisionClicked"
					class="division"
				>
					<div
						class="extend-wrapper"
						v-if="
							!controller.lastDivisionPage.value ||
							controller.divisionExtending.value
						"
					>
						<Transition name="fade" mode="out-in" :duration="250">
							<div
								v-if="!controller.divisionExtending.value"
								class="next-button-wrapper"
							>
								<button
									v-if="!controller.lastDivisionPage.value"
									@click="extendClicked"
									class="next-division"
								>
									Далее
								</button>
							</div>
							<div v-else class="spinner-wrapper">
								<PulseSpinner class="spinner"></PulseSpinner>
							</div>
						</Transition>
					</div>
				</Division>
				<Card
					v-else-if="!controller.divisionLoading.value && division && card"
					:card="card"
					:key="card.id"
					:path="division.path"
					:can-edit="division.canEdit"
					@save="onCardSave"
				></Card>

				<div
					v-else-if="controller.divisionLoading.value"
					class="spinner-wrapper"
				>
					<PulseSpinner class="spinner"></PulseSpinner>
				</div>
				<h2
					v-else-if="
						division === undefined &&
						card === undefined &&
						!controller.divisionLoading.value &&
						init
					"
				>
					Не заполнено
				</h2>
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

				.spinner-wrapper {
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

		.spinner-wrapper {
			display: flex;
			justify-content: center;
			align-items: center;

			width: 100%;
			height: fit-content;

			.spinner {
				width: 164px;
				height: 164px;

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
