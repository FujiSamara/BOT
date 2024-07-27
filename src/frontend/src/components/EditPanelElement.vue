<template>
	<form class="edit-panel-wrapper" @submit.prevent="$emit('submit')">
		<window-cross class="cross" @click="emit('close')"></window-cross>
		<div class="inputs-wrapper">
			<div
				class="input-wrapper"
				v-for="(field, index) in props.editor.fields"
				:key="field.name"
				@focusout="(event: FocusEvent) => onFocusOut(event, index)"
				@focusin="inputFocused[index] = true"
			>
				<p class="input-header">{{ field.name }}:</p>
				<border-input
					:id="field.name"
					:disabled="!field.canEdit"
					class="input"
					v-model:value="field.formattedField.value"
				></border-input>
				<Transition>
					<select-list
						v-if="field.selectList.value.length > 0 && inputFocused[index]"
						:selectList="field.selectList.value"
						@select="(index: number) => field.applySelection(index)"
					></select-list>
				</Transition>
			</div>
		</div>

		<purple-button class="button"
			><p style="margin: 0">Сохранить</p></purple-button
		>
	</form>
</template>
<script setup lang="ts">
import type { ExpenditureEditor } from "@/editor";
import { ref, Transition, type PropType } from "vue";

const props = defineProps({
	editor: {
		type: Object as PropType<ExpenditureEditor>,
		required: true,
	},
});
const inputFocused = ref(props.editor.fields.map((_) => false));
const onFocusOut = (event: FocusEvent, index: number) => {
	const relatedTarget = event.relatedTarget;
	if (relatedTarget instanceof HTMLElement) {
		if (relatedTarget.localName === "li") return;
	}
	inputFocused.value[index] = false;
};
const emit = defineEmits(["submit", "close"]);
</script>
<style scoped>
.edit-panel-wrapper {
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	background-color: #ffffff;
	border-radius: 20px;
	max-width: 725px;
	max-height: 100%;
	padding-bottom: 18px;
	gap: 20px;
	position: relative;
}
.inputs-wrapper {
	display: flex;
	flex-direction: column;
	align-items: flex-start;
	width: 100%;
	gap: 20px;
	overflow: auto;
	padding-left: 20px;
	padding-right: 20px;
}
.inputs-wrapper::-webkit-scrollbar {
	width: 5px;
	height: 5px;
	border-radius: 2000px;
}

.inputs-wrapper::-webkit-scrollbar-track {
	background-color: #e7e7e7;
}

.inputs-wrapper::-webkit-scrollbar-thumb:vertical {
	height: 10px;
	width: 5px;
	height: 15px !important;
	border-radius: 22px;
	background-color: #993ca6;
}
.input-wrapper {
	display: flex;
	flex-direction: column;
	justify-content: center;
	align-items: flex-start;
	width: 100%;
}
.input {
	background-color: #f6f6f6;
	width: 100%;
	height: 48px;
	margin-top: 10px;
	margin-bottom: 0;
	margin-left: 0;
	margin-right: 0;
	color: #292929;
	z-index: 1;
}
.input-header {
	color: #292929;
	font-family: Stolzl;
	font-weight: 500;
	font-size: 18px;
	margin: 0;
}
.button {
	width: calc(100% - 40px);
	background-color: #f5ecf6;
	color: #993ca6;
	font-size: 17px;
}

.v-enter-active,
.v-leave-active {
	transition: all 0.5s ease;
}

.v-enter-from,
.v-leave-to {
	max-height: 0;
}

.cross {
	align-self: flex-end;
	z-index: 2;
	position: relative;
	top: 15px;
	right: 15px;
}
</style>
