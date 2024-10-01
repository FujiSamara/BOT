<template>
	<div class="wrapper">
		<BorderInput
			placeholder="Фильтр"
			v-model:value="value"
			disabled
		></BorderInput>
		<ClickableIcon
			@click="listVisible = !listVisible"
			class="icon"
			img-src="/img/filter.svg"
		></ClickableIcon>
		<div class="list-wrapper">
			<Transition>
				<SelectList
					@select="onClick"
					class="list"
					v-if="listVisible"
					:select-list="list.filter((el) => el !== value)"
				></SelectList>
			</Transition>
		</div>
	</div>
</template>
<script setup lang="ts">
import { ref } from "vue";
import SelectList from "../UI/SelectList.vue";
import BorderInput from "../UI/BorderInput.vue";
import ClickableIcon from "../UI/ClickableIcon.vue";
import { FilterSchema } from "@/table";

const listVisible = ref(false);

const emit = defineEmits<{
	(e: "submit", filter: Array<FilterSchema>): void;
}>();

const value = ref("Не выбрано");
const list = ref([
	"Не выбрано",
	"Согласование ЦФО",
	"Согласование ЦЗ",
	"Согласование РЦЗ",
	"Согласование КРУ",
	"Согласование бух.",
	"Согласование кассир",
	"Выплачена",
	"Отклонена",
]);

const onClick = async (index: number) => {
	value.value = list.value.filter((el) => el !== value.value)[index];
	listVisible.value = false;

	let filters: Array<FilterSchema> = [];

	switch (value.value) {
		case "Согласование ЦФО":
			filters = [
				{
					column: "fac_state",
					value: "pending_approval",
				},
			];
			break;

		case "Согласование ЦЗ":
			filters = [
				{
					column: "cc_state",
					value: "pending_approval",
				},
			];
			break;

		case "Согласование РЦЗ":
			filters = [
				{
					column: "cc_supervisor_state",
					value: "pending_approval",
				},
			];
			break;

		case "Согласование КРУ":
			filters = [
				{
					column: "kru_state",
					value: "pending_approval",
				},
			];
			break;

		case "Согласование бух.":
			filters = [
				{
					column: "accountant_cash_state",
					value: "pending_approval",
					groups: [0],
				},
				{
					column: "accountant_card_state",
					value: "pending_approval",
					groups: [0],
				},
			];
			break;

		case "Согласование кассир":
			filters = [
				{
					column: "teller_cash_state",
					value: "pending_approval",
					groups: [0],
				},
				{
					column: "teller_card_state",
					value: "pending_approval",
					groups: [0],
				},
			];
			break;

		case "Выплачена":
			filters = [
				{
					column: "teller_cash_state",
					value: "approved",
					groups: [0],
				},
				{
					column: "teller_card_state",
					value: "approved",
					groups: [0],
				},
			];
			break;
		case "Отклонена":
			filters = [
				{
					column: "fac_state",
					value: "denied",
					groups: [0],
				},
				{
					column: "cc_state",
					value: "denied",
					groups: [0],
				},
				{
					column: "cc_supervisor_state",
					value: "denied",
					groups: [0],
				},
				{
					column: "kru_state",
					value: "denied",
					groups: [0],
				},
				{
					column: "accountant_cash_state",
					value: "denied",
					groups: [0],
				},
				{
					column: "accountant_card_state",
					value: "denied",
					groups: [0],
				},
				{
					column: "teller_cash_state",
					value: "denied",
					groups: [0],
				},
				{
					column: "teller_card_state",
					value: "denied",
					groups: [0],
				},
			];
			break;
	}

	emit("submit", filters);
};
</script>
<style scoped>
.wrapper {
	display: flex;
	gap: 10px;
}
.icon {
	width: 20px;
}
.list-wrapper {
	position: absolute;
	top: 100%;
	min-width: 200px;
	z-index: 2;
	background-color: #ffffff;
}

.v-enter-active,
.v-leave-active {
	transition: all 0.5s ease;
}

.v-enter-from,
.v-leave-to {
	max-height: 0;
}
</style>
