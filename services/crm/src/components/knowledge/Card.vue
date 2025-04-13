<script setup lang="ts">
import { computed, PropType, Ref, ref } from "vue";

import DishCardView from "@/components/knowledge/DishCard.vue";
import CommonCard from "@/components/knowledge/BusinessCard.vue";
import EditCard from "@/components/knowledge/EditCard.vue";
import DivisionPath from "@/components/knowledge/DivisionPath.vue";

import {
	BusinessCard,
	Card,
	CardType,
	DishCard,
	FileLinkSchema,
} from "@/components/knowledge/types";
import {
	Field,
	getCardFields,
	toCardUpdate,
} from "@/components/knowledge/editor";
import { toast } from "vue3-toastify";
import { DocumentSchema } from "@/types";

const props = defineProps({
	path: {
		type: String,
		required: true,
	},
	card: {
		type: Object as PropType<Card>,
		required: true,
	},
	canEdit: {
		type: Boolean,
	},
});

const editMode = ref(false);
const emits = defineEmits<{
	(e: "save", card_update: any): void;
}>();
const switchMode = () => {
	editMode.value = !editMode.value;
	if (editMode.value) {
		fields.value = getCardFields(props.card);
	}
};
const onSave = (val: Field[]) => {
	const result = toCardUpdate(props.card.type, val);

	if (result["materials"] !== undefined) {
		let oldMaterials: FileLinkSchema[] = [];
		if (props.card.type === CardType.dish) {
			if (dish.value.materials !== undefined) {
				oldMaterials = dish.value.materials?.materials;
			}
		} else {
			oldMaterials = business.value.materials;
		}

		const materials: DocumentSchema[] = result["materials"];
		for (const material of materials) {
			if (oldMaterials.some((val) => val.name === material.name)) {
				toast.error(`Файл ${material.name} уже существует!`);
				return;
			}
		}
	}

	fields.value = [];
	switchMode();
	emits("save", result);
};
const fields: Ref<Field[]> = ref([]);

const dish = computed(() => props.card as DishCard);
const business = computed(() => props.card as BusinessCard);
</script>
<template>
	<div class="k-card">
		<div class="card-head">
			<DivisionPath :path="props.path"></DivisionPath>
			<Transition name="fade" mode="out-in">
				<div
					class="wrapper"
					v-if="props.canEdit && !editMode"
					@click="switchMode"
				>
					<div class="edit"></div>
				</div>
				<div class="wrapper" v-else-if="props.canEdit" @click="switchMode">
					<div class="cross"></div>
				</div>
			</Transition>
		</div>
		<Transition name="fade" mode="out-in">
			<div class="cards" v-if="!editMode">
				<DishCardView
					v-if="props.card.type == CardType.dish"
					:key="props.card.id"
					:card="dish"
				></DishCardView>
				<CommonCard
					v-if="props.card.type == CardType.business"
					:key="props.card.id"
					:card="business"
				></CommonCard>
			</div>

			<EditCard
				v-else
				:fields="getCardFields(props.card)"
				@save="onSave"
			></EditCard>
		</Transition>
	</div>
</template>
<style scoped lang="scss">
.k-card {
	display: flex;
	flex-direction: column;

	width: 100%;
	height: fit-content;
	gap: 32px;

	.card-head {
		display: flex;
		flex-direction: row;

		align-items: center;
		justify-content: space-between;

		.wrapper {
			display: flex;
			justify-content: center;
			align-items: center;
			border-radius: 4px;
			width: 24px;
			height: 24px;
			transition: background-color 0.25s;
			cursor: pointer;

			.edit {
				@include editMark();
			}

			.cross {
				@include editMark();

				mask: url("@/assets/icons/cross.svg") no-repeat;
			}

			&:hover {
				background-color: $main-accent-blue;

				.edit,
				.cross {
					color: $main-white;
				}
			}
		}
	}
}
</style>
