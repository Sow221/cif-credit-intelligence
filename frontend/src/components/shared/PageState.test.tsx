import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import i18n from "@/locales";
import { PageState } from "./PageState";

describe("PageState", () => {
  beforeEach(async () => {
    await i18n.changeLanguage("fr");
  });

  it("renders a loading skeleton while status is loading", () => {
    render(<PageState status="loading">content</PageState>);
    expect(screen.getByLabelText("Chargement...")).toBeInTheDocument();
    expect(screen.queryByText("content")).not.toBeInTheDocument();
  });

  it("renders an error state with the given error", () => {
    render(
      <PageState status="error" error="Boom">
        content
      </PageState>,
    );
    expect(screen.getByRole("alert")).toHaveTextContent("Boom");
    expect(
      screen.getByText("Impossible de charger les données. Veuillez réessayer."),
    ).toBeInTheDocument();
  });

  it("renders the retry button only when onRetry is provided", async () => {
    const user = userEvent.setup();
    const onRetry = vi.fn();
    render(
      <PageState status="error" error="Boom" onRetry={onRetry}>
        content
      </PageState>,
    );
    await user.click(screen.getByText("error.retry"));
    expect(onRetry).toHaveBeenCalledTimes(1);
  });

  it("renders the forbidden error", () => {
    render(<PageState status="forbidden">content</PageState>);
    expect(screen.getByText("Vous n'avez pas les permissions nécessaires.")).toBeInTheDocument();
  });

  it("renders children on success", () => {
    render(<PageState status="success">content</PageState>);
    expect(screen.getByText("content")).toBeInTheDocument();
  });

  it("renders the provided empty state on success", () => {
    render(
      <PageState status="success" emptyState={<p>custom-empty</p>}>
        content
      </PageState>,
    );
    expect(screen.getByText("custom-empty")).toBeInTheDocument();
    expect(screen.queryByText("content")).not.toBeInTheDocument();
  });

  it("renders the default empty state when status is idle and a title is set", () => {
    render(
      <PageState status="idle" defaultEmptyTitle="Aucune demande">
        content
      </PageState>,
    );
    expect(screen.getByText("Aucune demande")).toBeInTheDocument();
    expect(screen.queryByText("content")).not.toBeInTheDocument();
  });

  it("renders children when status is idle without a default empty title", () => {
    render(<PageState status="idle">content</PageState>);
    expect(screen.getByText("content")).toBeInTheDocument();
  });
});
