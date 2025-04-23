<script setup lang="ts">
import { PropType, ref } from "vue";

import DefaultButton from "@/components/UI-new/DefaultButton.vue";
import EntitySelect from "@/components/entity/EntitySelect.vue";

import { RowEditor } from "@/hooks/rowEditorHook";
import { BidSchema } from "@/types";
import { SelectType, StringInputEntity } from "@/components/entity";
import { BidTable } from "@/pages/panels/bid";

const props = defineProps({
	editor: {
		type: Object as PropType<RowEditor<BidSchema, BidTable>>,
		required: true,
	},
});
const editor = props.editor;

const reasonEntity = new StringInputEntity(true, "Причина отказа");
reasonEntity.withTitle = true;
const declineActive = ref(false);
const declineConfirmDisabled = ref(false);

const accept = async () => {
	if (editor.modelIndex.value === undefined) {
		throw Error("Model index is undefined");
	}
	await editor.table.approve(editor.modelIndex.value, true);
	editor.close();
};

const decline = async () => {
	if (editor.modelIndex.value === undefined) {
		throw Error("Model index is undefined");
	}
	editor.showCustom.value = true;
	declineActive.value = true;
	editor.title.value = "Отклонить заявку";
};

const confirmDecline = async () => {
	if (editor.modelIndex.value === undefined) {
		throw Error("Model index is undefined");
	}

	if (!reasonEntity.completed.value) {
		const currentError = reasonEntity.overrideError.value;
		reasonEntity.overrideError.value = "Обязательное поле";
		setTimeout(() => {
			reasonEntity.overrideError.value = currentError;
		}, 2000);
		return;
	}

	declineConfirmDisabled.value = true;

	await editor.table.reject(
		editor.modelIndex.value,
		true,
		reasonEntity.getResult(),
	);
	editor.close();
};
</script>

<template>
	<div class="cc-wrapper">
		<div class="controls" v-if="!declineActive">
			<DefaultButton
				class="decline"
				@click="decline"
				title="Отказать"
			></DefaultButton>
			<DefaultButton
				class="accept"
				@click="accept"
				title="Согласовать"
			></DefaultButton>
		</div>
		<div class="decline-controls" v-else>
			<EntitySelect
				:entity="reasonEntity"
				:select-type="SelectType.Input"
				class="select-wrapper"
			></EntitySelect>
			<DefaultButton
				class="decline"
				@click="confirmDecline"
				title="Отказать"
				:disabled="declineConfirmDisabled"
			></DefaultButton>
		</div>
	</div>
</template>

<style scoped lang="scss">
.cc-wrapper {
	display: flex;
	min-width: fit-content;
	flex-grow: 1;

	.controls {
		display: flex;
		flex-direction: row;
		justify-content: space-between;
		flex-grow: 1;

		gap: 27px;

		.decline {
			background-color: $sec-arrantion-red;
		}

		.accept {
			background-color: $stroke-green;
		}
	}
	.decline-controls {
		display: flex;
		flex-direction: column;
		width: 1024px;
		gap: 24px;

		.decline {
			background-color: $sec-arrantion-red;
		}
	}
}
</style>
