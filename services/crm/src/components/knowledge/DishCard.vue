<script setup lang="ts">
import { computed, PropType, Ref, ref, watch } from "vue";
import PulseSpinner from "@/components/UI-new/PulseSpinner.vue";
import CardMaterials from "./CardMaterials.vue";
import { DishCard, IngredientSchema } from "@/components/knowledge/types";

const props = defineProps({
	card: {
		type: Object as PropType<DishCard>,
		required: true,
	},
	canEdit: {
		type: Boolean,
	},
});
const emits = defineEmits<{
	(e: "delete", materialId: number): void;
}>();
const isCompound = ref(true);

const parseIngridients = (ingredients: IngredientSchema[]) => {
	const temp = {
		sauces: ingredients
			.filter((ing) => ing.title.toLocaleLowerCase().includes("соус"))
			.sort((a, b) => -a.title.length + b.title.length),
		compounds: ingredients
			.filter((ing) => !ing.title.toLocaleLowerCase().includes("соус"))
			.sort((a, b) => -a.title.length + b.title.length),
	};

	return {
		group1: {
			sauces: temp.sauces.filter((_, i) => i % 2 === 0),
			compounds: temp.compounds.filter((_, i) => i % 2 === 0),
		},
		group2: {
			sauces: temp.sauces.filter((_, i) => i % 2 === 1),
			compounds: temp.compounds.filter((_, i) => i % 2 === 1),
		},
	};
};

const groups = computed(() => {
	if (props.card.modifiers === undefined) return [];

	return [...props.card.modifiers];
});

const modifierIndexes: Ref<number[]> = ref([]);
watch(
	groups,
	() => {
		modifierIndexes.value = groups.value.map((_) => 0);
	},
	{ immediate: true },
);

const ingridients = computed(() => {
	const result: IngredientSchema[] = [];

	if (!modifierIndexes.value.length) {
		return parseIngridients(result);
	}

	for (let index = 0; index < groups.value.length; index++) {
		const group = groups.value[index];
		const choosedIndex = modifierIndexes.value[index];
		const choosedModfier = group.modifiers[choosedIndex];

		result.push(...choosedModfier.ingredients);
	}

	return parseIngridients(result);
});
const ingridientsExist = computed(() => {
	return (
		ingridients.value.group1.compounds.length +
			ingridients.value.group2.compounds.length !==
		0
	);
});

const saucesExist = computed(() => {
	return (
		ingridients.value.group1.sauces.length +
		ingridients.value.group2.sauces.length
	);
});
const compoundsExist = computed(() => {
	return (
		ingridients.value.group1.compounds.length +
		ingridients.value.group2.compounds.length
	);
});

const filtersExist = computed(() => {
	return groups.value.some((modifier) => modifier.modifiers.length > 1);
});

const video = computed(() => {
	if (props.card.materials === undefined) return;
	return props.card.materials.video;
});

const convertAmount = (amount: number): string => {
	return amount >= 1 ? `${amount} шт` : `${Math.round(amount * 1000)} г`;
};
</script>
<template>
	<div class="card-wrapper">
		<h2 class="title">{{ props.card.title }}</h2>
		<main class="content">
			<img :src="props.card.image" />
			<div class="info-wrapper">
				<Transition name="fade" mode="out-in">
					<div v-if="props.card.modifiers !== undefined" class="info">
						<div class="controls">
							<div class="switch">
								<button
									@click="isCompound = true"
									v-if="groups.length"
									:class="{ active: isCompound }"
								>
									Состав
								</button>
								<button
									@click="isCompound = false"
									:class="{ active: !isCompound }"
								>
									Рецепт
								</button>
							</div>
							<div class="tools"></div>
						</div>

						<Transition name="fade" mode="out-in">
							<div v-if="isCompound && groups.length" class="compound-wrapper">
								<div
									class="filters"
									v-if="filtersExist"
									v-for="(group, groupIndex) in groups"
								>
									<span class="title">Фильтры</span>
									<ul v-if="group.modifiers.length > 1">
										<li v-for="(modifier, i) in group.modifiers">
											<button
												@click="modifierIndexes[groupIndex] = i"
												:class="{ active: i === modifierIndexes[groupIndex] }"
											>
												{{ modifier.title }}
											</button>
										</li>
									</ul>
								</div>
								<Transition name="fade" mode="out-in">
									<div
										v-if="ingridientsExist"
										:key="modifierIndexes.reduce((f, s) => f + s)"
										class="compound-inner"
									>
										<div class="part" v-if="saucesExist">
											<span class="title">Соус</span>
											<div class="group">
												<ul>
													<li v-for="sauce in ingridients.group1.sauces">
														<span class="li-title">{{ sauce.title }}</span>
														<span class="li-amount">{{
															convertAmount(sauce.amount)
														}}</span>
													</li>
												</ul>
												<ul>
													<li v-for="sauce in ingridients.group2.sauces">
														<span class="li-title">{{ sauce.title }}</span>
														<span class="li-amount">{{
															convertAmount(sauce.amount)
														}}</span>
													</li>
												</ul>
											</div>
										</div>
										<div class="part" v-if="compoundsExist">
											<span class="title">Состав</span>
											<div class="group">
												<ul>
													<li v-for="compound in ingridients.group1.compounds">
														<span class="li-title">{{ compound.title }}</span>
														<span class="li-amount">{{
															convertAmount(compound.amount)
														}}</span>
													</li>
												</ul>
												<ul>
													<li v-for="compound in ingridients.group2.compounds">
														<span class="li-title">{{ compound.title }}</span>
														<span class="li-amount">{{
															convertAmount(compound.amount)
														}}</span>
													</li>
												</ul>
											</div>
										</div>
									</div>
								</Transition>
							</div>
							<div v-else class="recept-wrapper">
								<span
									class="recept"
									v-for="line in props.card.description.split('\n')"
									>{{ line }}<br
								/></span>
							</div>
						</Transition>
					</div>
					<div v-else class="spinner-wrapper">
						<PulseSpinner class="spinner"></PulseSpinner>
					</div>
				</Transition>
			</div>
		</main>
		<Transition name="fade" mode="out-in">
			<footer v-if="props.card.materials" class="materials">
				<video v-if="video" class="video" controls>
					<source :src="video.url" type="video/mp4" />
					{{ video.name }}
				</video>
				<CardMaterials
					v-if="props.card.materials.materials.length"
					:materials="props.card.materials.materials"
					@delete="
						(index: number) =>
							emits('delete', props.card.materials!.materials[index].id)
					"
					:can-delete="props.canEdit"
				></CardMaterials>
			</footer>
			<div v-else class="spinner-wrapper">
				<PulseSpinner class="spinner"></PulseSpinner>
			</div>
		</Transition>
	</div>
</template>
<style scoped lang="scss">
@import "bootstrap/scss/functions";
@import "bootstrap/scss/variables";
@import "bootstrap/scss/mixins";

@import url("./style.scss");

.card-wrapper {
	.content {
		display: flex;
		flex-direction: row;

		gap: 16px;

		padding: 16px;
		background-color: $main-white;

		img {
			width: 480px;
			height: 480px;
		}

		.info-wrapper {
			position: relative;
			display: flex;
			flex-grow: 1;

			overflow-x: auto;
			max-height: 100%;
			height: 480px;
			width: 100%;

			padding: 16px;
			background-color: $bg-light-blue;

			.info {
				display: flex;
				flex-direction: column;

				gap: 16px;

				width: 100%;
				max-height: 100%;
				height: 100%;

				overflow-y: auto;

				.controls {
					display: flex;
					flex-direction: row;

					justify-content: space-between;
					align-items: center;
					width: 100%;

					height: 40px;

					.switch {
						display: flex;
						flex-direction: row;

						gap: 8px;

						button {
							width: 112px;
							height: 39px;
							color: $main-accent-blue;

							border: 1px solid $sec-dark-gray-25;
							background-color: $bg-light-blue;
							border-radius: 4px;

							&.active,
							&:hover {
								border-color: $main-accent-blue;
								background-color: $main-white;
							}

							transition:
								border-color 0.25s,
								background-color 0.25s;
						}
					}

					.tools {
						height: 28px;
						width: 68px;
					}
				}

				.title {
					font-family: Wix Madefor Display;
					font-weight: 700;
					font-size: 16px;
				}

				.filters {
					display: flex;
					flex-direction: column;

					max-width: 100%;
					gap: 16px;

					ul {
						display: flex;
						flex-direction: row;
						width: fit-content;
						max-width: 100%;
						flex-wrap: wrap;

						gap: 8px;

						border-radius: 16px;
						background-color: $main-white;

						button {
							min-width: 84px;
							height: 42px;
							padding: 8px 14px;

							background-color: $main-white;
							border: none;
							color: $main-accent-blue;
							border-radius: 24px;
							transition: background-color 0.25s;

							&.active,
							&:hover {
								color: $main-white;
								background-color: $sec-gray-blue;
							}
						}
					}
				}

				.compound-wrapper {
					display: flex;
					flex-direction: column;

					gap: 16px;
					height: 100%;

					.compound-inner {
						display: flex;
						flex-direction: column;

						height: 100%;

						gap: 16px;

						.part {
							display: flex;
							flex-direction: column;

							gap: 16px;

							ul {
								display: flex;
								flex-direction: column;

								gap: 6px;
							}

							li {
								display: flex;
								flex-direction: row;

								align-items: center;

								gap: 24px;
								width: fit-content;

								padding: 6px 12px;
								border-radius: 8px;

								background-color: $main-white;
							}

							.group {
								display: flex;
								flex-direction: row;

								gap: 24px;
							}

							.li-title {
								width: 256px;
							}
							.li-amount {
								text-align: right;
								width: 56px;
							}
						}
					}
				}

				.recept-wrapper {
					width: 100%;
					height: fit-content;

					border-radius: 16px;
					padding: 24px;
					background-color: $main-white;

					.recept {
						font-family: Wix Madefor Display;
						font-weight: 400;
						font-size: 14px;
					}
				}
			}
		}

		@include media-breakpoint-down(xxl) {
			flex-direction: column;
			align-items: center;
		}

		@include media-breakpoint-down(xl) {
			.info-wrapper {
				.info {
					.compound-wrapper {
						.compound-inner {
							.part {
								.group {
									flex-direction: column;
								}
							}
						}
					}
				}
			}
		}
	}

	.materials {
		.video {
			width: 100%;
			height: 480px;
		}
	}
}
</style>
